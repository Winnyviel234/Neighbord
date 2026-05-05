from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

class BaseModel(ABC):
    """Base model interface"""
    id: Optional[UUID]

class BaseRepository(ABC):
    """Base repository interface"""
    
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def get_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def update(self, id: UUID, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        pass