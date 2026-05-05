from typing import List, Optional
from uuid import UUID
from .repository import DirectivaRepository
from .model import (
    CargoCreate, CargoUpdate, CargoAsignacion, CargoAsignacionUpdate,
    CargoResponse, CargoAsignacionResponse, DirectivaResponse
)


class DirectivaService:
    """Service layer for directiva (board) business logic"""

    def __init__(self, repository: DirectivaRepository):
        self.repository = repository

    # Cargo Management
    async def create_cargo(self, cargo: CargoCreate) -> CargoResponse:
        """Create new cargo position"""
        result = await self.repository.create_cargo(cargo)
        if not result:
            raise ValueError("Failed to create cargo")
        return CargoResponse(**result)

    async def get_cargo(self, cargo_id: UUID) -> CargoResponse:
        """Get cargo by ID"""
        cargo = await self.repository.get_cargo_by_id(cargo_id)
        if not cargo:
            raise ValueError(f"Cargo {cargo_id} not found")
        return CargoResponse(**cargo)

    async def get_sector_cargos(self, sector_id: UUID) -> List[CargoResponse]:
        """Get all cargos in a sector"""
        cargos = await self.repository.get_all_cargos(sector_id)
        return [CargoResponse(**c) for c in cargos]

    async def update_cargo(self, cargo_id: UUID, cargo: CargoUpdate) -> CargoResponse:
        """Update cargo"""
        result = await self.repository.update_cargo(cargo_id, cargo)
        if not result:
            raise ValueError(f"Cargo {cargo_id} not found")
        return CargoResponse(**result)

    async def delete_cargo(self, cargo_id: UUID) -> bool:
        """Delete cargo"""
        return await self.repository.delete_cargo(cargo_id)

    # Assignment Management
    async def assign_cargo(self, asignacion: CargoAsignacion) -> CargoAsignacionResponse:
        """Assign a user to a cargo position"""
        # Validate cargo exists
        await self.get_cargo(asignacion.cargo_id)
        
        # Check if user already has this cargo
        existing = await self.repository.get_user_cargos(asignacion.user_id, asignacion.sector_id)
        for cargo in existing:
            if cargo["cargo_id"] == asignacion.cargo_id:
                raise ValueError(f"User already has cargo {asignacion.cargo_id}")
        
        result = await self.repository.asignar_cargo(asignacion)
        if not result:
            raise ValueError("Failed to assign cargo")
        return CargoAsignacionResponse(**result)

    async def get_assignment(self, asignacion_id: UUID) -> CargoAsignacionResponse:
        """Get assignment by ID"""
        assignment = await self.repository.get_asignacion_by_id(asignacion_id)
        if not assignment:
            raise ValueError(f"Assignment {asignacion_id} not found")
        return CargoAsignacionResponse(**assignment)

    async def get_active_assignments(self, sector_id: Optional[UUID] = None) -> List[dict]:
        """Get all active assignments"""
        return await self.repository.get_active_asignaciones(sector_id)

    async def get_user_assignments(self, user_id: UUID, sector_id: Optional[UUID] = None) -> List[dict]:
        """Get all active assignments for a user"""
        return await self.repository.get_user_cargos(user_id, sector_id)

    async def update_assignment(self, asignacion_id: UUID, update: CargoAsignacionUpdate) -> CargoAsignacionResponse:
        """Update assignment"""
        result = await self.repository.update_asignacion(asignacion_id, update)
        if not result:
            raise ValueError(f"Assignment {asignacion_id} not found")
        return CargoAsignacionResponse(**result)

    async def terminate_assignment(self, asignacion_id: UUID) -> CargoAsignacionResponse:
        """Terminate assignment"""
        result = await self.repository.terminar_asignacion(asignacion_id)
        if not result:
            raise ValueError(f"Assignment {asignacion_id} not found")
        return CargoAsignacionResponse(**result)

    # Directiva Structure
    async def get_directiva(self, sector_id: UUID) -> DirectivaResponse:
        """Get complete directiva structure for a sector"""
        miembros = await self.repository.get_directiva(sector_id)
        return DirectivaResponse(
            sector_id=sector_id,
            miembros=miembros,
            created_at=None  # Puede ser timestamp del sector
        )

    async def initialize_sector_directiva(self, sector_id: UUID) -> List[CargoResponse]:
        """Initialize default cargos for new sector"""
        cargos = await self.repository.initialize_default_cargos(sector_id)
        return [CargoResponse(**c) for c in cargos]

    async def get_directiva_stats(self, sector_id: UUID) -> dict:
        """Get statistics about sector directiva"""
        assignments = await self.repository.get_active_asignaciones(sector_id)
        cargos = await self.repository.get_all_cargos(sector_id)
        
        return {
            "total_cargos": len(cargos),
            "assigned_positions": len(assignments),
            "vacant_positions": len(cargos) - len(assignments),
            "miembros": assignments,
            "occupancy_rate": (len(assignments) / len(cargos) * 100) if cargos else 0
        }
