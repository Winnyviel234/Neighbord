from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["live"])




REAL_MAP_CENTER = {
    "lat": -16.5,
    "lng": -68.15,
    "zoom": 16,
    "name": "Sector comunitario",
}

CHAT_MESSAGES = []

DIRECTIVA_MESSAGES = [
    {"id": "directiva-1", "asunto": "Consulta por luminaria", "mensaje": "Solicito revisar el poste frente a la sede vecinal.", "estado": "recibido", "fecha": "2026-04-30T10:00:00+00:00"},
]

NOTIFICATIONS = [
    {"id": "noti-1", "tipo": "Sistema", "titulo": "Canal en vivo activo", "mensaje": "Chat y mapa sincronizados en tiempo real.", "fecha": "2026-04-30T12:00:00+00:00", "estado": "nuevo"},
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class LiveManager:
    def __init__(self):
        self.connections: set[WebSocket] = set()
        self.users: dict[WebSocket, dict] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.add(websocket)
        self.users[websocket] = {"id": str(uuid4()), "nombre": "Vecino"}
        await websocket.send_json({
            "type": "snapshot",
            "chat": CHAT_MESSAGES[-80:],
            "directiva": DIRECTIVA_MESSAGES[-80:],
            "notifications": NOTIFICATIONS[-20:],
            "realMap": REAL_MAP_CENTER,
            "presence": self.presence(),
        })
        await self.broadcast({"type": "presence:update", "presence": self.presence()})

    def disconnect(self, websocket: WebSocket):
        self.connections.discard(websocket)
        self.users.pop(websocket, None)

    def presence(self) -> list[dict]:
        seen = {}
        for user in self.users.values():
            seen[user["id"]] = user
        return list(seen.values())

    async def broadcast(self, payload: dict):
        dead: list[WebSocket] = []
        for websocket in self.connections:
            try:
                await websocket.send_json(payload)
            except Exception:
                dead.append(websocket)
        for websocket in dead:
            self.disconnect(websocket)


manager = LiveManager()


@router.get("/live/status")
def live_status():
    return {
        "status": "ok",
        "connections": len(manager.connections),
        "messages": len(CHAT_MESSAGES),
        "map": REAL_MAP_CENTER,
    }


def notification(tipo: str, titulo: str, mensaje: str) -> dict:
    item = {
        "id": f"noti-{uuid4()}",
        "tipo": tipo,
        "titulo": titulo,
        "mensaje": mensaje,
        "fecha": now_iso(),
        "estado": "nuevo",
    }
    NOTIFICATIONS.insert(0, item)
    del NOTIFICATIONS[40:]
    return item


@router.websocket("/ws/live")
async def live_socket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            payload = await websocket.receive_json()
            action = payload.get("type")

            if action == "chat:send":
                message = {
                    "id": f"chat-{uuid4()}",
                    "autor": payload.get("autor") or "Vecino",
                    "mensaje": (payload.get("mensaje") or "").strip(),
                    "fecha": now_iso(),
                }
                if not message["mensaje"]:
                    continue
                CHAT_MESSAGES.append(message)
                del CHAT_MESSAGES[:-100]
                noti = notification("Comunidad", "Nuevo mensaje vecinal", f"{message['autor']} escribio en el chat.")
                await manager.broadcast({"type": "chat:new", "message": message})
                await manager.broadcast({"type": "notification:new", "notification": noti})

            elif action == "presence:join":
                user_name = (payload.get("nombre") or "Vecino").strip()[:80]
                manager.users[websocket] = {"id": payload.get("user_id") or manager.users[websocket]["id"], "nombre": user_name}
                await manager.broadcast({"type": "presence:update", "presence": manager.presence()})

            elif action == "chat:typing":
                await manager.broadcast({
                    "type": "chat:typing",
                    "autor": (payload.get("autor") or "Vecino").strip()[:80],
                    "isTyping": bool(payload.get("isTyping")),
                })

            elif action == "directiva:send":
                message = {
                    "id": f"directiva-{uuid4()}",
                    "asunto": (payload.get("asunto") or "").strip(),
                    "mensaje": (payload.get("mensaje") or "").strip(),
                    "estado": "recibido",
                    "fecha": now_iso(),
                }
                if not message["asunto"] or not message["mensaje"]:
                    continue
                DIRECTIVA_MESSAGES.insert(0, message)
                del DIRECTIVA_MESSAGES[100:]
                noti = notification("Directiva", "Mensaje recibido", message["asunto"])
                await manager.broadcast({"type": "directiva:new", "message": message})
                await manager.broadcast({"type": "notification:new", "notification": noti})



            elif action == "map:real:update":
                center = payload.get("center") or {}
                try:
                    REAL_MAP_CENTER["lat"] = float(center.get("lat"))
                    REAL_MAP_CENTER["lng"] = float(center.get("lng"))
                    REAL_MAP_CENTER["zoom"] = int(center.get("zoom") or REAL_MAP_CENTER["zoom"])
                    REAL_MAP_CENTER["name"] = (center.get("name") or "Sector comunitario").strip()[:120]
                except (TypeError, ValueError):
                    continue
                noti = notification("Mapa", "Mapa real actualizado", REAL_MAP_CENTER["name"])
                await manager.broadcast({"type": "map:real:update", "center": REAL_MAP_CENTER})
                await manager.broadcast({"type": "notification:new", "notification": noti})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        try:
            await manager.broadcast({"type": "presence:update", "presence": manager.presence()})
        except Exception:
            pass
    except Exception:
        manager.disconnect(websocket)
        try:
            await manager.broadcast({"type": "presence:update", "presence": manager.presence()})
        except Exception:
            pass
