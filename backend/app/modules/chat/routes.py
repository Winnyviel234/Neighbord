from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional
from uuid import UUID
from app.core.security import get_current_user
from app.modules.chat.service import ChatService
from app.modules.chat.model import ChatRoomCreate, ChatRoomResponse, MessageCreate, MessageResponse, WebSocketMessage

router = APIRouter(prefix="/chat", tags=["chat"])

chat_service = ChatService()

# In-memory storage for active connections (in production, use Redis)
active_connections: Dict[str, List[WebSocket]] = {}

@router.get("/rooms", response_model=List[ChatRoomResponse])
async def get_rooms(user: dict = Depends(get_current_user)):
    """Get accessible chat rooms"""
    return await chat_service.get_rooms(user)

@router.get("/rooms/{room_id}", response_model=ChatRoomResponse)
async def get_room(room_id: UUID, user: dict = Depends(get_current_user)):
    """Get specific chat room"""
    return await chat_service.get_room(room_id, user)

@router.post("/rooms", response_model=ChatRoomResponse)
async def create_room(
    payload: ChatRoomCreate,
    user: dict = Depends(get_current_user)
):
    """Create new chat room (admin/directiva only)"""
    return await chat_service.create_room(payload, user)

@router.delete("/rooms/{room_id}")
async def delete_room(
    room_id: UUID,
    user: dict = Depends(get_current_user)
):
    """Delete chat room (admin only)"""
    return await chat_service.delete_room(room_id, user)

@router.get("/rooms/{room_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    room_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    user: dict = Depends(get_current_user)
):
    """Get messages for a room"""
    return await chat_service.get_messages(room_id, user, limit)

@router.post("/rooms/{room_id}/messages", response_model=MessageResponse)
async def send_message(
    room_id: UUID,
    payload: MessageCreate,
    user: dict = Depends(get_current_user)
):
    """Send message to room"""
    message = await chat_service.send_message(room_id, payload, user)
    
    # Broadcast to WebSocket connections
    await broadcast_to_room(str(room_id), {
        "type": "message",
        "content": payload.content,
        "user_name": user.get("nombre", "Usuario"),
        "created_at": message.created_at.isoformat() if message.created_at else None
    })
    
    return message

async def broadcast_to_room(room_id: str, message: dict):
    """Broadcast message to all connections in a room"""
    if room_id in active_connections:
        for connection in active_connections[room_id]:
            try:
                await connection.send_json(message)
            except:
                # Remove dead connections
                active_connections[room_id].remove(connection)

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    # Add to active connections
    if room_id not in active_connections:
        active_connections[room_id] = []
    active_connections[room_id].append(websocket)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "system",
            "content": "Conectado al chat",
            "user_name": "Sistema"
        })
        
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            message = WebSocketMessage(**data)
            
            if message.type == "join":
                await websocket.send_json({
                    "type": "system",
                    "content": f"{message.user_name} se unió al chat",
                    "user_name": "Sistema"
                })
            elif message.type == "leave":
                await websocket.send_json({
                    "type": "system",
                    "content": f"{message.user_name} salió del chat",
                    "user_name": "Sistema"
                })
            elif message.type == "message":
                # Broadcast the message to all in room
                await broadcast_to_room(room_id, {
                    "type": "message",
                    "content": message.content,
                    "user_name": message.user_name
                })
    
    except WebSocketDisconnect:
        # Remove from active connections
        if room_id in active_connections and websocket in active_connections[room_id]:
            active_connections[room_id].remove(websocket)