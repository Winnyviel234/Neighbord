from typing import List, Dict, Any
from uuid import UUID
from fastapi import HTTPException
from app.modules.complaints.repository import ComplaintRepository
from app.modules.complaints.model import ComplaintCreate, ComplaintUpdate, ComplaintResponse, ComplaintCommentCreate
from app.core.supabase import table

class ComplaintService:
    def __init__(self):
        self.repo = ComplaintRepository()
    
    async def get_complaint(self, complaint_id: UUID, current_user: Dict[str, Any]) -> ComplaintResponse:
        """Get complaint by ID with permission check"""
        complaint = await self.repo.get_by_id(complaint_id)
        if not complaint:
            raise HTTPException(404, "Queja no encontrada")
        
        # Users can see their own complaints, admin/directiva can see all
        if (str(complaint["usuario_id"]) != current_user["id"] and 
            current_user.get("role_name") not in ["admin", "directiva"]):
            raise HTTPException(403, "No tienes permisos para ver esta queja")
        
        return ComplaintResponse(**complaint)
    
    async def get_complaints(self, current_user: Dict[str, Any], filters: Dict[str, Any] = None) -> List[ComplaintResponse]:
        """Get complaints with filtering"""
        # Build filters based on user role
        query_filters = {}
        
        if current_user.get("role_name") not in ["admin", "directiva"]:
            # Regular users only see their own complaints
            query_filters["user_id"] = current_user["id"]
        else:
            # Admin/directiva can filter by sector
            if current_user.get("sector_id"):
                query_filters["sector_id"] = current_user["sector_id"]
        
        # Apply additional filters
        if filters:
            query_filters.update(filters)
        
        complaints = await self.repo.get_all(query_filters)
        return [ComplaintResponse(**complaint) for complaint in complaints]
    
    async def create_complaint(self, data: ComplaintCreate, current_user: Dict[str, Any]) -> ComplaintResponse:
        """Create new complaint"""
        complaint_data = {
            "usuario_id": current_user["id"],
            "titulo": data.title,
            "descripcion": data.description,
            "categoria": data.category,
            "prioridad": data.priority,
            "estado": "abierta"
        }
        
        complaint = await self.repo.create(complaint_data)
        return await self.get_complaint(complaint["id"], current_user)
    
    async def update_complaint(self, complaint_id: UUID, data: ComplaintUpdate, current_user: Dict[str, Any]) -> ComplaintResponse:
        """Update complaint with permission check"""
        complaint = await self.repo.get_by_id(complaint_id)
        if not complaint:
            raise HTTPException(404, "Queja no encontrada")
        
        # Check permissions
        is_owner = str(complaint["usuario_id"]) == current_user["id"]
        is_admin = current_user.get("role_name") in ["admin", "directiva"]
        
        if not (is_owner or is_admin):
            raise HTTPException(403, "No tienes permisos para actualizar esta queja")
        
        # Only admin can change assignment and status
        update_data = data.model_dump(exclude_unset=True)
        if "assigned_to" in update_data or "status" in update_data:
            if not is_admin:
                raise HTTPException(403, "Solo admin/directiva puede asignar o cambiar estado")
        
        updated = await self.repo.update(complaint_id, update_data)
        if not updated:
            raise HTTPException(404, "Queja no encontrada")
        
        return await self.get_complaint(complaint_id, current_user)
    
    async def delete_complaint(self, complaint_id: UUID, current_user: Dict[str, Any]) -> Dict[str, str]:
        """Delete complaint (admin only)"""
        if current_user.get("role_name") != "admin":
            raise HTTPException(403, "Solo el administrador puede eliminar quejas")
        
        success = await self.repo.delete(complaint_id)
        if not success:
            raise HTTPException(404, "Queja no encontrada")
        
        return {"message": "Queja eliminada exitosamente"}
    
    async def add_comment(self, complaint_id: UUID, data: ComplaintCommentCreate, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Add comment to complaint"""
        # Verify user can access this complaint
        complaint = await self.repo.get_by_id(complaint_id)
        if not complaint:
            raise HTTPException(404, "Queja no encontrada")
        
        is_owner = str(complaint["usuario_id"]) == current_user["id"]
        is_admin = current_user.get("role_name") in ["admin", "directiva"]
        is_assigned = str(complaint.get("assigned_to")) == current_user["id"]
        
        if not (is_owner or is_admin or is_assigned):
            raise HTTPException(403, "No tienes permisos para comentar en esta queja")
        
        comment = await self.repo.add_comment(complaint_id, current_user["id"], data.comment)
        
        # Update complaint timestamp
        await self.repo.update(complaint_id, {})
        
        return {
            "id": comment["id"],
            "comment": comment["comment"],
            "user_name": current_user.get("nombre", "Usuario"),
            "created_at": comment["created_at"]
        }
    
    async def get_comments(self, complaint_id: UUID, current_user: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get comments for a complaint"""
        # Verify access
        complaint = await self.repo.get_by_id(complaint_id)
        if not complaint:
            raise HTTPException(404, "Queja no encontrada")
        
        is_owner = str(complaint["usuario_id"]) == current_user["id"]
        is_admin = current_user.get("role_name") in ["admin", "directiva"]
        is_assigned = str(complaint.get("assigned_to")) == current_user["id"]
        
        if not (is_owner or is_admin or is_assigned):
            raise HTTPException(403, "No tienes permisos para ver los comentarios")
        
        return await self.repo.get_comments(complaint_id)