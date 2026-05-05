from typing import List, Dict, Any
from uuid import UUID
from fastapi import HTTPException
from app.modules.meetings.repository import MeetingRepository
from app.modules.meetings.model import MeetingCreate, MeetingUpdate, MeetingResponse, AttendanceResponse

class MeetingService:
    def __init__(self):
        self.repo = MeetingRepository()
    
    async def get_all_meetings(self, filters: Dict[str, Any] = None) -> List[MeetingResponse]:
        """Get all accessible meetings"""
        meetings = await self.repo.get_all(filters)
        return [MeetingResponse(**m) for m in meetings]
    
    async def get_meeting(self, meeting_id: UUID) -> MeetingResponse:
        """Get specific meeting"""
        meeting = await self.repo.get_by_id(meeting_id)
        if not meeting:
            raise HTTPException(404, "Reunión no encontrada")
        return MeetingResponse(**meeting)
    
    async def create_meeting(self, data: MeetingCreate, current_user: Dict[str, Any]) -> MeetingResponse:
        """Create meeting (admin/directiva only)"""
        if current_user.get("role_name") not in ["admin", "directiva"]:
            raise HTTPException(403, "No tienes permisos para crear reuniones")
        
        meeting_data = {
            "titulo": data.titulo,
            "descripcion": data.descripcion,
            "fecha": data.fecha,
            "lugar": data.lugar,
            "tipo": data.tipo,
            "estado": "programada",
            "creado_por": current_user["id"]
        }
        
        meeting = await self.repo.create(meeting_data)
        return await self.get_meeting(meeting["id"])
    
    async def update_meeting(self, meeting_id: UUID, data: MeetingUpdate, current_user: Dict[str, Any]) -> MeetingResponse:
        """Update meeting (admin/directiva only)"""
        if current_user.get("role_name") not in ["admin", "directiva"]:
            raise HTTPException(403, "No tienes permisos para actualizar reuniones")
        
        meeting = await self.repo.update(meeting_id, data.model_dump(exclude_unset=True))
        if not meeting:
            raise HTTPException(404, "Reunión no encontrada")
        
        return await self.get_meeting(meeting_id)
    
    async def delete_meeting(self, meeting_id: UUID, current_user: Dict[str, Any]) -> Dict[str, str]:
        """Delete meeting (admin only)"""
        if current_user.get("role_name") != "admin":
            raise HTTPException(403, "Solo el administrador puede eliminar reuniones")
        
        success = await self.repo.delete(meeting_id)
        if not success:
            raise HTTPException(404, "Reunión no encontrada")
        
        return {"message": "Reunión eliminada"}
    
    async def register_attendance(self, meeting_id: UUID, current_user: Dict[str, Any]) -> AttendanceResponse:
        """Register user attendance"""
        meeting = await self.repo.get_by_id(meeting_id)
        if not meeting:
            raise HTTPException(404, "Reunión no encontrada")
        
        # Check if already attended
        if await self.repo.is_attended(meeting_id, current_user["id"]):
            raise HTTPException(409, "Ya has registrado tu asistencia")
        
        attendance = await self.repo.add_attendance(meeting_id, current_user["id"])
        return AttendanceResponse(**attendance)
    
    async def get_attendances(self, meeting_id: UUID) -> List[AttendanceResponse]:
        """Get attendances for a meeting"""
        meeting = await self.repo.get_by_id(meeting_id)
        if not meeting:
            raise HTTPException(404, "Reunión no encontrada")
        
        attendances = await self.repo.get_attendances(meeting_id)
        return [AttendanceResponse(**a) for a in attendances]