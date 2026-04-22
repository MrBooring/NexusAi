from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import WebSocket


class DeviceHubService:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.devices: Dict[str, Dict[str, Any]] = {}
        self.message_log: List[Dict[str, Any]] = []

    async def connect(self, device_id: str, websocket: WebSocket, device_type: str = "unknown"):
        await websocket.accept()
        self.connections[device_id] = websocket
        self.devices[device_id] = {
            "device_id": device_id,
            "device_type": device_type,
            "status": "connected",
            "connected_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
        }
        await self.broadcast_event({
            "event": "device_connected",
            "device": self.devices[device_id],
        }, exclude=device_id)

    async def disconnect(self, device_id: str):
        self.connections.pop(device_id, None)
        if device_id in self.devices:
            self.devices[device_id]["status"] = "disconnected"
            self.devices[device_id]["last_seen"] = datetime.now().isoformat()
            await self.broadcast_event({
                "event": "device_disconnected",
                "device": self.devices[device_id],
            }, exclude=device_id)

    async def update_device(self, device_id: str, payload: Optional[Dict[str, Any]] = None):
        if device_id not in self.devices:
            return
        self.devices[device_id]["last_seen"] = datetime.now().isoformat()
        if payload:
            self.devices[device_id].update(payload)

    async def send_to_device(self, device_id: str, message: Dict[str, Any]):
        websocket = self.connections.get(device_id)
        if websocket:
            await websocket.send_json(message)

    async def broadcast_event(self, message: Dict[str, Any], exclude: Optional[str] = None):
        stale = []
        for device_id, websocket in self.connections.items():
            if exclude and device_id == exclude:
                continue
            try:
                await websocket.send_json(message)
            except Exception:
                stale.append(device_id)
        for device_id in stale:
            self.connections.pop(device_id, None)

    def record_message(self, sender: str, payload: Dict[str, Any]):
        entry = {
            "sender": sender,
            "payload": payload,
            "timestamp": datetime.now().isoformat(),
        }
        self.message_log.append(entry)
        self.message_log = self.message_log[-50:]
        return entry

    def get_status(self) -> Dict[str, Any]:
        active = [device for device in self.devices.values() if device.get("status") == "connected"]
        return {
            "active_devices": len(active),
            "known_devices": len(self.devices),
            "devices": list(self.devices.values()),
            "recent_messages": self.message_log[-10:],
        }


device_hub_service = DeviceHubService()
