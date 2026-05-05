from typing import List, Dict, Any
from uuid import UUID
from fastapi import HTTPException
from app.modules.chat.repository import ChatRepository
from app.modules.chat.model import ChatRoomCreate, ChatRoomResponse, MessageCreate, MessageResponse

class ChatService:
    def __init__(self):
        self.repo = ChatRepository()
    
    async def get_rooms(self, current_user: Dict[str, Any]) -> List[ChatRoomResponse]:
        """Get accessible chat rooms"""
        user_sector_id = current_user.get("sector_id")
        rooms = await self.repo.get_all_rooms(user_sector_id)
        return [ChatRoomResponse(**room) for room in rooms]
    
    async def get_room(self, room_id: UUID, current_user: Dict[str, Any]) -> ChatRoomResponse:
        """Get specific chat room"""
        user_sector_id = current_user.get("sector_id")
        if not await self.repo.can_access_room(room_id, user_sector_id):
            raise HTTPException(403, "No tienes acceso a esta sala de chat")
        
        room = await self.repo.get_room_by_id(room_id)
        if not room:
            raise HTTPException(404, "Sala de chat no encontrada")
        
        return ChatRoomResponse(**room)
    
    async def create_room(self, data: ChatRoomCreate, current_user: Dict[str, Any]) -> ChatRoomResponse:
        """Create new chat room (admin/directiva only)"""
        if current_user.get("role_name") not in ["admin", "directiva"]:
            raise HTTPException(403, "Solo admin/directiva puede crear salas de chat")
        
        # If sector-specific room, verify user is in that sector or admin
        if data.sector_id and current_user.get("role_name") != "admin":
            if str(data.sector_id) != str(current_user.get("sector_id")):
                raise HTTPException(403, "No puedes crear salas en otros sectores")
        
        room_data = {
            "sector_id": str(data.sector_id) if data.sector_id else None,
            "name": data.name,
            "type": data.type
        }
        
        room = await self.repo.create_room(room_data)
        return ChatRoomResponse(**room)
    
    async def delete_room(self, room_id: UUID, current_user: Dict[str, Any]) -> Dict[str, str]:
        """Delete chat room (admin only)"""
        if current_user.get("role_name") != "admin":
            raise HTTPException(403, "Solo el administrador puede eliminar salas de chat")
        
        success = await self.repo.delete_room(room_id)
        if not success:
            raise HTTPException(404, "Sala de chat no encontrada")
        
        return {"message": "Sala de chat eliminada exitosamente"}
    
    async def get_messages(self, room_id: UUID, current_user: Dict[str, Any], limit: int = 50) -> List[MessageResponse]:
        """Get messages for a room"""
        user_sector_id = current_user.get("sector_id")
        if not await self.repo.can_access_room(room_id, user_sector_id):
            raise HTTPException(403, "No tienes acceso a esta sala de chat")
        
        messages = await self.repo.get_messages(room_id, limit)
        return [MessageResponse(**msg) for msg in messages]
    
    async def send_message(self, room_id: UUID, data: MessageCreate, current_user: Dict[str, Any]) -> MessageResponse:
        """Send message to room"""
        user_sector_id = current_user.get("sector_id")
        if not await self.repo.can_access_room(room_id, user_sector_id):
            raise HTTPException(403, "No tienes acceso a esta sala de chat")
        
        message_data = {
            "room_id": str(room_id),
            "user_id": current_user["id"],
            "content": data.content
        }
        
        message = await self.repo.create_message(message_data)
        message["user_name"] = current_user.get("nombre", "Usuario")
        
        return MessageResponse(**message)