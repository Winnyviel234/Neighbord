from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.modules.base import BaseRepository
from .model import CargoCreate, CargoUpdate, CargoAsignacion, CargoAsignacionUpdate, DEFAULT_CARGOS


class DirectivaRepository(BaseRepository):
    """Repository for directiva (board management) data access"""

    async def create_cargo(self, cargo: CargoCreate) -> dict:
        """Create a new cargo position"""
        query = """
        INSERT INTO cargos (sector_id, name, descripcion, permisos)
        VALUES (%s, %s, %s, %s)
        RETURNING *
        """
        return await self.execute(
            query,
            (
                str(cargo.sector_id),
                cargo.name,
                cargo.descripcion,
                cargo.permisos
            )
        )

    async def get_cargo_by_id(self, cargo_id: UUID) -> Optional[dict]:
        """Get cargo by ID"""
        query = "SELECT * FROM cargos WHERE id = %s"
        return await self.fetch_one(query, (str(cargo_id),))

    async def get_all_cargos(self, sector_id: Optional[UUID] = None) -> List[dict]:
        """Get all cargos with optional sector filter"""
        if sector_id:
            query = "SELECT * FROM cargos WHERE sector_id = %s ORDER BY name"
            return await self.fetch_all(query, (str(sector_id),))
        
        query = "SELECT * FROM cargos ORDER BY sector_id, name"
        return await self.fetch_all(query, ())

    async def update_cargo(self, cargo_id: UUID, cargo: CargoUpdate) -> Optional[dict]:
        """Update cargo"""
        updates = []
        values = []

        if cargo.name:
            updates.append("name = %s")
            values.append(cargo.name)
        if cargo.descripcion:
            updates.append("descripcion = %s")
            values.append(cargo.descripcion)
        if cargo.permisos:
            updates.append("permisos = %s")
            values.append(cargo.permisos)

        if not updates:
            return await self.get_cargo_by_id(cargo_id)

        updates.append("updated_at = now()")
        query = f"UPDATE cargos SET {', '.join(updates)} WHERE id = %s RETURNING *"
        values.append(str(cargo_id))

        return await self.execute(query, tuple(values))

    async def delete_cargo(self, cargo_id: UUID) -> bool:
        """Delete cargo"""
        query = "DELETE FROM cargos WHERE id = %s"
        result = await self.execute(query, (str(cargo_id),))
        return result is not None

    async def asignar_cargo(self, asignacion: CargoAsignacion) -> dict:
        """Assign a user to a cargo position"""
        query = """
        INSERT INTO cargo_asignaciones (user_id, cargo_id, sector_id, fecha_inicio, activo)
        VALUES (%s, %s, %s, %s, true)
        RETURNING *
        """
        return await self.execute(
            query,
            (
                str(asignacion.user_id),
                str(asignacion.cargo_id),
                str(asignacion.sector_id),
                asignacion.fecha_inicio or datetime.now()
            )
        )

    async def get_asignacion_by_id(self, asignacion_id: UUID) -> Optional[dict]:
        """Get assignment by ID"""
        query = "SELECT * FROM cargo_asignaciones WHERE id = %s"
        return await self.fetch_one(query, (str(asignacion_id),))

    async def get_active_asignaciones(self, sector_id: Optional[UUID] = None) -> List[dict]:
        """Get active assignments"""
        if sector_id:
            query = """
            SELECT ca.*, c.name as cargo_name, u.nombre, u.email
            FROM cargo_asignaciones ca
            JOIN cargos c ON ca.cargo_id = c.id
            JOIN usuarios u ON ca.user_id = u.id
            WHERE ca.sector_id = %s AND ca.activo = true
            ORDER BY c.name
            """
            return await self.fetch_all(query, (str(sector_id),))
        
        query = """
        SELECT ca.*, c.name as cargo_name, u.nombre, u.email
        FROM cargo_asignaciones ca
        JOIN cargos c ON ca.cargo_id = c.id
        JOIN usuarios u ON ca.user_id = u.id
        WHERE ca.activo = true
        ORDER BY ca.sector_id, c.name
        """
        return await self.fetch_all(query, ())

    async def get_user_cargos(self, user_id: UUID, sector_id: Optional[UUID] = None) -> List[dict]:
        """Get all active cargos for a user"""
        if sector_id:
            query = """
            SELECT ca.*, c.name, c.permisos, c.descripcion
            FROM cargo_asignaciones ca
            JOIN cargos c ON ca.cargo_id = c.id
            WHERE ca.user_id = %s AND ca.sector_id = %s AND ca.activo = true
            """
            return await self.fetch_all(query, (str(user_id), str(sector_id)))
        
        query = """
        SELECT ca.*, c.name, c.permisos, c.descripcion
        FROM cargo_asignaciones ca
        JOIN cargos c ON ca.cargo_id = c.id
        WHERE ca.user_id = %s AND ca.activo = true
        """
        return await self.fetch_all(query, (str(user_id),))

    async def update_asignacion(self, asignacion_id: UUID, update: CargoAsignacionUpdate) -> Optional[dict]:
        """Update assignment"""
        updates = []
        values = []

        if update.fecha_fin:
            updates.append("fecha_fin = %s")
            values.append(update.fecha_fin)
        if update.activo is not None:
            updates.append("activo = %s")
            values.append(update.activo)

        if not updates:
            return await self.get_asignacion_by_id(asignacion_id)

        updates.append("updated_at = now()")
        query = f"UPDATE cargo_asignaciones SET {', '.join(updates)} WHERE id = %s RETURNING *"
        values.append(str(asignacion_id))

        return await self.execute(query, tuple(values))

    async def terminar_asignacion(self, asignacion_id: UUID) -> Optional[dict]:
        """Terminate assignment (set as inactive)"""
        query = """
        UPDATE cargo_asignaciones 
        SET activo = false, fecha_fin = now(), updated_at = now() 
        WHERE id = %s 
        RETURNING *
        """
        return await self.execute(query, (str(asignacion_id),))

    async def initialize_default_cargos(self, sector_id: UUID) -> List[dict]:
        """Initialize default cargos for a new sector"""
        results = []
        for cargo_data in DEFAULT_CARGOS:
            query = """
            INSERT INTO cargos (sector_id, name, descripcion, permisos)
            VALUES (%s, %s, %s, %s)
            RETURNING *
            """
            result = await self.execute(
                query,
                (
                    str(sector_id),
                    cargo_data["name"],
                    cargo_data["descripcion"],
                    cargo_data["permisos"]
                )
            )
            results.append(result)
        return results

    async def get_directiva(self, sector_id: UUID) -> dict:
        """Get complete directiva structure for a sector"""
        query = """
        SELECT 
            ca.id, ca.user_id, ca.cargo_id, ca.fecha_inicio, ca.fecha_fin, ca.activo,
            c.name as cargo_name, c.permisos,
            u.nombre, u.email, u.telefono
        FROM cargo_asignaciones ca
        JOIN cargos c ON ca.cargo_id = c.id
        JOIN usuarios u ON ca.user_id = u.id
        WHERE ca.sector_id = %s AND ca.activo = true
        ORDER BY c.name
        """
        return await self.fetch_all(query, (str(sector_id),))

    async def count_active_assignments(self, sector_id: UUID) -> int:
        """Count active cargo assignments in sector"""
        query = "SELECT COUNT(*) as count FROM cargo_asignaciones WHERE sector_id = %s AND activo = true"
        result = await self.fetch_one(query, (str(sector_id),))
        return result["count"] if result else 0
