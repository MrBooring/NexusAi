import asyncio
import importlib
import importlib.util
import io
import os
import tempfile
import uuid
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional, Dict, Any

import numpy as np

from app.config.settings import settings

executor = ThreadPoolExecutor(max_workers=2)


class VoiceService:
    def __init__(self):
        self._whisper_model = None
        self._tts_model = None
        self._use_pyttsx3 = False
        self.audio_dir = Path("./data/audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def _load_whisper(self):
        try:
            whisper = importlib.import_module("whisper")
        except Exception as exc:
            raise RuntimeError(
                "Whisper is not installed. Install dependencies from requirements.txt to enable transcription."
            ) from exc

        if self._whisper_model is None:
            try:
                self._whisper_model = whisper.load_model(settings.whisper_model)
            except Exception as exc:
                raise RuntimeError(
                    f"Failed to load Whisper model '{settings.whisper_model}'. The model files may not be installed or accessible."
                ) from exc
        return self._whisper_model

    def _load_tts(self):
        try:
            tts_api = importlib.import_module("TTS.api")
        except Exception as exc:
            raise RuntimeError(
                "Coqui TTS is not installed or cannot be imported. Install dependencies from requirements.txt to enable speech output."
            ) from exc

        if self._tts_model is None:
            try:
                self._tts_model = tts_api.TTS(model_name=settings.tts_model, progress_bar=False, gpu=False)
            except Exception as exc:
                raise RuntimeError(
                    f"Failed to load TTS model '{settings.tts_model}'. The model files may not be installed or accessible. "
                    "Please check TTS installation or use text-only mode."
                ) from exc
        return self._tts_model

    def _decode_wav_bytes(self, audio_bytes: bytes) -> np.ndarray:
        try:
            with wave.open(io.BytesIO(audio_bytes), "rb") as wav_file:
                sample_rate = wav_file.getframerate()
                sample_width = wav_file.getsampwidth()
                channels = wav_file.getnchannels()
                frames = wav_file.readframes(wav_file.getnframes())
        except wave.Error as exc:
            raise RuntimeError("The recorded audio is not a valid WAV file.") from exc

        if sample_width != 2:
            raise RuntimeError("Only 16-bit PCM WAV input is supported for direct transcription.")

        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        if channels > 1:
            audio = audio.reshape(-1, channels).mean(axis=1)

        if sample_rate <= 0:
            raise RuntimeError("The WAV recording is missing a valid sample rate.")

        target_rate = 16000
        if sample_rate != target_rate and audio.size:
            duration = audio.shape[0] / sample_rate
            target_length = max(1, int(round(duration * target_rate)))
            source_positions = np.linspace(0.0, duration, num=audio.shape[0], endpoint=False)
            target_positions = np.linspace(0.0, duration, num=target_length, endpoint=False)
            audio = np.interp(target_positions, source_positions, audio).astype(np.float32)

        return audio

    async def transcribe_audio_bytes(self, audio_bytes: bytes, filename: Optional[str] = None) -> str:
        suffix = Path(filename or "audio.webm").suffix or ".webm"
        loop = asyncio.get_event_loop()
        model = await loop.run_in_executor(executor, self._load_whisper)

        if suffix.lower() == ".wav":
            audio_array = await loop.run_in_executor(executor, lambda: self._decode_wav_bytes(audio_bytes))
            result = await loop.run_in_executor(
                executor,
                lambda: model.transcribe(audio_array, fp16=False)
            )
            return (result.get("text") or "").strip()

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name

        try:
            result = await loop.run_in_executor(
                executor,
                lambda: model.transcribe(temp_path, fp16=False)
            )
            return (result.get("text") or "").strip()
        except FileNotFoundError as exc:
            raise RuntimeError(
                "Audio transcription for this format needs FFmpeg. Use the built-in recorder on the Friday page, "
                "or install FFmpeg for additional audio formats."
            ) from exc
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass

    async def synthesize_speech(self, text: str) -> Dict[str, Any]:
        """Synthesize speech using Coqui TTS first, then a fallback engine if needed."""
        filename = f"voice-{uuid.uuid4().hex}.wav"
        output_path = self.audio_dir / filename
        loop = asyncio.get_event_loop()
        
        try:
            # Try Coqui TTS first if not already flagged as unavailable
            if not self._use_pyttsx3:
                try:
                    tts_model = await loop.run_in_executor(executor, self._load_tts)
                    await loop.run_in_executor(
                        executor,
                        lambda: tts_model.tts_to_file(text=text, file_path=str(output_path))
                    )
                    # Verify file was created
                    if output_path.exists():
                        return {
                            "filename": filename,
                            "path": str(output_path),
                            "audio_url": f"/voice/audio/{filename}",
                            "engine": "coqui"
                        }
                except Exception as coqui_error:
                    print(f"Coqui TTS failed, falling back to pyttsx3: {coqui_error}")
                    self._use_pyttsx3 = True
            
            # Fallback engine
            return await self._synthesize_with_pyttsx3(text, output_path)
            
        except Exception as e:
            error_msg = str(e)
            raise RuntimeError(f"All TTS engines failed: {error_msg}") from e

    async def _synthesize_with_pyttsx3(self, text: str, output_path: Path) -> Dict[str, Any]:
        """Fallback synthesis using gTTS when the local engine is unavailable."""
        loop = asyncio.get_event_loop()
        
        def _generate_with_gtts():
            try:
                from gtts import gTTS
                import os
                
                # Create gTTS object (English, slow speed for clarity)
                tts = gTTS(text=text, lang='en', slow=True)
                
                # Ensure output directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save to file
                tts.save(str(output_path))
                
                if os.path.exists(str(output_path)) and os.path.getsize(str(output_path)) > 0:
                    return str(output_path)
                else:
                    raise RuntimeError(f"gTTS failed to create audio file at {output_path}")
                    
            except Exception as e:
                raise RuntimeError(f"gTTS synthesis failed: {str(e)}") from e
        
        try:
            output_file = await loop.run_in_executor(executor, _generate_with_gtts)
            
            return {
                "filename": os.path.basename(output_file),
                "path": output_file,
                "audio_url": f"/voice/audio/{os.path.basename(output_file)}",
                "engine": "gtts_fallback"
            }
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"Fallback TTS (gTTS) failed: {str(e)}") from e

    async def get_status(self) -> Dict[str, Any]:
        def check_module(name: str) -> bool:
            try:
                return importlib.util.find_spec(name) is not None
            except Exception:
                return False

        return {
            "whisper_installed": check_module("whisper"),
            "tts_installed": check_module("TTS.api"),
            "gtts_installed": check_module("gtts"),
            "using_fallback": self._use_pyttsx3,
            "whisper_model": settings.whisper_model,
            "tts_model": settings.tts_model,
            "engines": {
                "primary": "coqui_tts",
                "fallback": "gtts",
                "current": "gtts" if self._use_pyttsx3 else "coqui_tts"
            }
        }


voice_service = VoiceService()
