from typing import Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query

from app.services.device_hub import device_hub_service

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("")
async def list_devices():
    return device_hub_service.get_status()


@router.get("/{device_id}")
async def get_device(device_id: str):
    status = device_hub_service.get_status()
    for device in status["devices"]:
        if device["device_id"] == device_id:
            return device
    raise HTTPException(status_code=404, detail="Device not found")


@router.websocket("/ws/{device_id}")
async def device_socket(
    websocket: WebSocket,
    device_id: str,
    device_type: Optional[str] = Query(default="unknown"),
):
    await device_hub_service.connect(device_id, websocket, device_type=device_type or "unknown")
    try:
        await websocket.send_json({
            "event": "welcome",
            "device_id": device_id,
            "devices": device_hub_service.get_status()["devices"],
        })

        while True:
            payload = await websocket.receive_json()
            await device_hub_service.update_device(device_id)
            message = device_hub_service.record_message(device_id, payload)

            if payload.get("event") == "ping":
                await device_hub_service.send_to_device(device_id, {
                    "event": "pong",
                    "timestamp": message["timestamp"],
                })
                continue

            await device_hub_service.broadcast_event({
                "event": "device_message",
                "message": message,
            }, exclude=None)
    except WebSocketDisconnect:
        await device_hub_service.disconnect(device_id)
    except Exception:
        await device_hub_service.disconnect(device_id)
