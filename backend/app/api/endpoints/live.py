from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends, HTTPException
from jose import jwt

from app.core.config import settings
from app.core.supabase import table
from app.modules.auth.repository import DEFAULT_ROLES

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

DIRECTIVA_CHAT_MESSAGES = []

NOTIFICATIONS = [
    {"id": "noti-1", "tipo": "Sistema", "titulo": "Canal en vivo activo", "mensaje": "Chat y mapa sincronizados en tiempo real.", "fecha": "2026-04-30T12:00:00+00:00", "estado": "nuevo"},
]

DIRECTIVA_ROLES = {"admin", "superadmin", "directiva", "tesorero", "vocero", "secretaria"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except Exception:
        return None


def is_directiva_role(role: str | None) -> bool:
    if not role:
        return False
    return role in DIRECTIVA_ROLES


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


class DirectivaChatManager:
    def __init__(self):
        self.connections: set[WebSocket] = set()
        self.users: dict[WebSocket, dict] = {}

    async def connect(self, websocket: WebSocket, user: dict):
        await websocket.accept()
        self.connections.add(websocket)
        self.users[websocket] = user
        await websocket.send_json({
            "type": "snapshot",
            "messages": DIRECTIVA_CHAT_MESSAGES[-100:],
            "presence": self.presence(),
        })
        await self.broadcast({"type": "presence:update", "presence": self.presence()})

    def disconnect(self, websocket: WebSocket):
        self.connections.discard(websocket)
        self.users.pop(websocket, None)

    def presence(self) -> list[dict]:
        seen = {}
        for user in self.users.values():
            user_id = user.get("id") or user.get("user_id")
            if user_id:
                seen[user_id] = {"id": user_id, "nombre": user.get("nombre") or "Directivo"}
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
directiva_manager = DirectivaChatManager()


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


def resolve_user_role(user: dict) -> tuple[str, list]:
    role_name = user.get("rol", "vecino")
    role_permissions = DEFAULT_ROLES.get(role_name, DEFAULT_ROLES["vecino"])["permissions"]
    if user.get("role_id"):
        try:
            role_result = table("roles").select("name, permissions").eq("id", user["role_id"]).single().execute()
            if role_result.data:
                role_name = role_result.data.get("name", role_name)
                role_permissions = role_result.data.get("permissions", role_permissions)
        except Exception:
            pass

    super_email = settings.super_admin_email or settings.admin_email
    if super_email and str(user.get("email", "")).strip().lower() == str(super_email).strip().lower():
        role_name = "superadmin"
        role_permissions = DEFAULT_ROLES["superadmin"]["permissions"]

    return role_name, role_permissions


def get_user_from_token(token: str) -> dict | None:
    payload = decode_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    try:
        result = table("usuarios").select("*").eq("id", user_id).single().execute()
        if not result.data:
            return None
        user = result.data
        role_name, role_permissions = resolve_user_role(user)
        user["role_name"] = role_name
        user["role_permissions"] = role_permissions
        return user
    except Exception:
        return None


@router.get("/directiva/check")
def check_directiva_access(user: dict = Depends(get_user_from_token)):
    """Verifica si el usuario tiene acceso al chat de directiva."""
    if not user:
        return {"access": False, "message": "No autenticado"}
    if not is_directiva_role(user.get("role_name")):
        return {"access": False, "message": "No eres miembro de la directiva"}
    return {"access": True, "user": {"id": user.get("id"), "nombre": user.get("nombre"), "rol": user.get("role_name")}}


@router.get("/directiva/chat/history")
def get_directiva_chat_history(user: dict = Depends(get_user_from_token)):
    """Obtiene el historial del chat de directiva."""
    if not user or not is_directiva_role(user.get("role_name")):
        raise HTTPException(status_code=403, detail="Acceso denegado")
    return {"messages": DIRECTIVA_CHAT_MESSAGES[-100:]}


@router.websocket("/ws/directiva")
async def directiva_chat_socket(websocket: WebSocket, token: str = Query(...)):
    """WebSocket para el chat privado de la directiva."""
    user = get_user_from_token(token)
    if not user or not is_directiva_role(user.get("role_name")):
        await websocket.close(code=4001)
        return

    user_info = {
        "id": user.get("id"),
        "nombre": user.get("nombre") or "Directivo",
        "rol": user.get("role_name")
    }

    await directiva_manager.connect(websocket, user_info)
    try:
        while True:
            payload = await websocket.receive_json()
            action = payload.get("type")

            if action == "chat:send":
                message = {
                    "id": f"dc-{uuid4()}",
                    "usuario_id": user.get("id"),
                    "autor": user.get("nombre") or "Directivo",
                    "mensaje": (payload.get("mensaje") or "").strip(),
                    "fecha": now_iso(),
                }
                if not message["mensaje"]:
                    continue
                DIRECTIVA_CHAT_MESSAGES.append(message)
                del DIRECTIVA_CHAT_MESSAGES[:-200]
                await directiva_manager.broadcast({"type": "chat:new", "message": message})

            elif action == "presence:join":
                directiva_manager.users[websocket] = {
                    "id": user.get("id"),
                    "nombre": (payload.get("nombre") or user.get("nombre") or "Directivo").strip()[:80],
                }
                await directiva_manager.broadcast({"type": "presence:update", "presence": directiva_manager.presence()})

            elif action == "chat:typing":
                await directiva_manager.broadcast({
                    "type": "chat:typing",
                    "autor": (payload.get("autor") or user.get("nombre") or "Directivo").strip()[:80],
                    "isTyping": bool(payload.get("isTyping")),
                })

    except WebSocketDisconnect:
        directiva_manager.disconnect(websocket)
        try:
            await directiva_manager.broadcast({"type": "presence:update", "presence": directiva_manager.presence()})
        except Exception:
            pass
    except Exception:
        directiva_manager.disconnect(websocket)
        try:
            await directiva_manager.broadcast({"type": "presence:update", "presence": directiva_manager.presence()})
        except Exception:
            pass
