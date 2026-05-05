from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class Sector(BaseModel):
    id: Optional[UUID]
    name: str
    description: Optional[str] = None
    address: Optional[str] = None

class SectorCreate(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None

class SectorUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None

class SectorResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    address: Optional[str]