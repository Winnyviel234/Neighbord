from typing import List, Optional, Dict, Any
from uuid import UUID
from app.core.supabase import table

class VotingRepository:
    def __init__(self):
        self.votings_table = table("votaciones")
        self.votes_table = table("votos")
    
    async def get_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get all votings"""
        query = self.votings_table.select("""
            votaciones.*,
            usuarios.nombre as creado_por_nombre
        """)
        
        if filters:
            if filters.get("estado"):
                query = query.eq("estado", filters["estado"])
        
        result = query.execute()
        return result.data or []
    
    async def get_by_id(self, voting_id: UUID) -> Optional[Dict[str, Any]]:
        """Get voting by ID"""
        result = self.votings_table.select("""
            votaciones.*,
            usuarios.nombre as creado_por_nombre
        """).eq("id", str(voting_id)).single().execute()
        return result.data
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create voting"""
        result = self.votings_table.insert(data).execute()
        return result.data[0]
    
    async def update(self, voting_id: UUID, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update voting"""
        result = self.votings_table.update(data).eq("id", str(voting_id)).execute()
        return result.data[0] if result.data else None
    
    async def delete(self, voting_id: UUID) -> bool:
        """Delete voting"""
        result = self.votings_table.delete().eq("id", str(voting_id)).execute()
        return len(result.data) > 0
    
    async def vote(self, voting_id: UUID, user_id: UUID, opcion: str) -> Dict[str, Any]:
        """Record vote"""
        data = {
            "votacion_id": str(voting_id),
            "usuario_id": str(user_id),
            "opcion": opcion
        }
        result = self.votes_table.insert(data).execute()
        return result.data[0]
    
    async def get_votes(self, voting_id: UUID) -> List[Dict[str, Any]]:
        """Get all votes for a voting"""
        result = self.votes_table.select("""
            votos.*,
            usuarios.nombre as usuario_nombre
        """).eq("votacion_id", str(voting_id)).execute()
        return result.data or []
    
    async def get_vote_count(self, voting_id: UUID) -> dict:
        """Get vote count by option"""
        votes = await self.get_votes(voting_id)
        counts = {}
        for vote in votes:
            opcion = vote.get("opcion")
            counts[opcion] = counts.get(opcion, 0) + 1
        return counts
    
    async def has_voted(self, voting_id: UUID, user_id: UUID) -> bool:
        """Check if user already voted"""
        result = self.votes_table.select("id").eq("votacion_id", str(voting_id)).eq("usuario_id", str(user_id)).execute()
        return len(result.data) > 0