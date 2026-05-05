from typing import List, Dict, Any
from uuid import UUID
from fastapi import HTTPException
from app.modules.voting.repository import VotingRepository
from app.modules.voting.model import VotingCreate, VotingResponse, VoteResponse

class VotingService:
    def __init__(self):
        self.repo = VotingRepository()
    
    async def get_all_votings(self, filters: Dict[str, Any] = None) -> List[VotingResponse]:
        """Get all votings"""
        votings = await self.repo.get_all(filters)
        responses = []
        for v in votings:
            v["resultados"] = await self.repo.get_vote_count(v["id"])
            v["total_votos"] = sum(v["resultados"].values())
            responses.append(VotingResponse(**v))
        return responses
    
    async def get_voting(self, voting_id: UUID, current_user: Dict[str, Any]) -> VotingResponse:
        """Get specific voting"""
        voting = await self.repo.get_by_id(voting_id)
        if not voting:
            raise HTTPException(404, "Votación no encontrada")
        
        voting["resultados"] = await self.repo.get_vote_count(voting_id)
        voting["total_votos"] = sum(voting["resultados"].values())
        voting["ya_voto"] = await self.repo.has_voted(voting_id, current_user["id"])
        
        return VotingResponse(**voting)
    
    async def create_voting(self, data: VotingCreate, current_user: Dict[str, Any]) -> VotingResponse:
        """Create voting (admin/directiva only)"""
        if current_user.get("role_name") not in ["admin", "directiva"]:
            raise HTTPException(403, "No tienes permisos para crear votaciones")
        
        voting_data = {
            "titulo": data.titulo,
            "descripcion": data.descripcion,
            "fecha_inicio": data.fecha_inicio,
            "fecha_fin": data.fecha_fin,
            "opciones": data.opciones,  # Será convertido a JSONB en BD
            "estado": "activa",
            "creado_por": current_user["id"]
        }
        
        voting = await self.repo.create(voting_data)
        return await self.get_voting(voting["id"], current_user)
    
    async def vote(self, voting_id: UUID, opcion: str, current_user: Dict[str, Any]) -> VoteResponse:
        """Cast a vote"""
        voting = await self.repo.get_by_id(voting_id)
        if not voting:
            raise HTTPException(404, "Votación no encontrada")
        
        if voting["estado"] != "activa":
            raise HTTPException(409, "La votación no está activa")
        
        # Check if option is valid
        if opcion not in voting.get("opciones", []):
            raise HTTPException(400, "Opción de voto no válida")
        
        # Check if user already voted
        if await self.repo.has_voted(voting_id, current_user["id"]):
            raise HTTPException(409, "Ya has votado en esta votación")
        
        vote = await self.repo.vote(voting_id, current_user["id"], opcion)
        return VoteResponse(**vote)
    
    async def close_voting(self, voting_id: UUID, current_user: Dict[str, Any]) -> VotingResponse:
        """Close voting (admin only)"""
        if current_user.get("role_name") != "admin":
            raise HTTPException(403, "Solo el administrador puede cerrar votaciones")
        
        voting = await self.repo.update(voting_id, {"estado": "finalizada"})
        if not voting:
            raise HTTPException(404, "Votación no encontrada")
        
        return await self.get_voting(voting_id, current_user)