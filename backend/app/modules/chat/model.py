from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class ChatRoom(BaseModel):
    id: Optional[UUID]
    sector_id: Optional[UUID]
    name: str
    type: str = "sector"  # sector, commission
    created_at: Optional[datetime] = None

class ChatRoomCreate(BaseModel):
    sector_id: Optional[UUID] = None
    name: str
    type: str = "sector"

class ChatRoomResponse(BaseModel):
    id: UUID
    sector_id: Optional[UUID]
    name: str
    type: str
    created_at: datetime

class Message(BaseModel):
    id: Optional[UUID]
    room_id: UUID
    user_id: UUID
    content: str
    created_at: Optional[datetime] = None

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: UUID
    room_id: UUID
    user_id: UUID
    user_name: str
    content: str
    created_at: datetime

class WebSocketMessage(BaseModel):
    type: str  # join, leave, message
    room_id: Optional[str] = None
    content: Optional[str] = None
    user_name: Optional[str] = None