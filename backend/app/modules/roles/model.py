from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class RoleBase(BaseModel):
    name: str
    permissions: List[str]
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    permissions: Optional[List[str]] = None
    description: Optional[str] = None

class RoleResponse(RoleBase):
    id: UUID
    created_at: Optional[str] = None
