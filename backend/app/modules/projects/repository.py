from typing import List, Optional
from uuid import UUID
from datetime import date
from app.modules.base import BaseRepository
from .model import ProjectCreate, ProjectUpdate


class ProjectRepository(BaseRepository):
    """Repository for project data access"""

    async def create(self, project: ProjectCreate, user_id: UUID) -> dict:
        """Create a new project"""
        query = """
        INSERT INTO proyectos (sector_id, title, description, status, presupuesto_estimado,
                              fecha_inicio, fecha_fin_estimada, responsable_id, prioridad, created_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
        """
        return await self.execute(
            query,
            (
                str(project.sector_id),
                project.title,
                project.description,
                project.status,
                project.presupuesto_estimado,
                project.fecha_inicio,
                project.fecha_fin_estimada,
                str(project.responsable_id),
                project.prioridad,
                str(user_id)
            )
        )

    async def get_by_id(self, project_id: UUID) -> Optional[dict]:
        """Get project by ID"""
        query = "SELECT * FROM proyectos WHERE id = %s"
        return await self.fetch_one(query, (str(project_id),))

    async def get_all(self, sector_id: Optional[UUID] = None, status: Optional[str] = None) -> List[dict]:
        """Get all projects with optional filtering"""
        query = "SELECT * FROM proyectos WHERE 1=1"
        params = []

        if sector_id:
            query += " AND sector_id = %s"
            params.append(str(sector_id))

        if status:
            query += " AND status = %s"
            params.append(status)

        query += " ORDER BY prioridad DESC, fecha_inicio DESC"
        return await self.fetch_all(query, tuple(params))

    async def update(self, project_id: UUID, project: ProjectUpdate) -> Optional[dict]:
        """Update project"""
        updates = []
        values = []

        if project.title:
            updates.append("title = %s")
            values.append(project.title)
        if project.description:
            updates.append("description = %s")
            values.append(project.description)
        if project.status:
            updates.append("status = %s")
            values.append(project.status)
        if project.presupuesto_aprobado is not None:
            updates.append("presupuesto_aprobado = %s")
            values.append(project.presupuesto_aprobado)
        if project.fecha_fin_estimada:
            updates.append("fecha_fin_estimada = %s")
            values.append(project.fecha_fin_estimada)
        if project.responsable_id:
            updates.append("responsable_id = %s")
            values.append(str(project.responsable_id))
        if project.prioridad:
            updates.append("prioridad = %s")
            values.append(project.prioridad)

        if not updates:
            return await self.get_by_id(project_id)

        updates.append("updated_at = now()")
        query = f"UPDATE proyectos SET {', '.join(updates)} WHERE id = %s RETURNING *"
        values.append(str(project_id))

        return await self.execute(query, tuple(values))

    async def delete(self, project_id: UUID) -> bool:
        """Delete project (soft delete via status)"""
        query = "UPDATE proyectos SET status = 'cancelado', updated_at = now() WHERE id = %s"
        result = await self.execute(query, (str(project_id),))
        return result is not None

    async def get_by_sector(self, sector_id: UUID) -> List[dict]:
        """Get all projects in a sector"""
        query = "SELECT * FROM proyectos WHERE sector_id = %s AND status != 'cancelado' ORDER BY fecha_inicio DESC"
        return await self.fetch_all(query, (str(sector_id),))

    async def get_by_responsible(self, user_id: UUID) -> List[dict]:
        """Get projects managed by a user"""
        query = "SELECT * FROM proyectos WHERE responsable_id = %s AND status != 'cancelado' ORDER BY fecha_inicio DESC"
        return await self.fetch_all(query, (str(user_id),))

    async def add_expense(self, expense_data: dict) -> dict:
        """Add expense to project"""
        query = """
        INSERT INTO project_expenses (project_id, descripcion, monto, fecha, categoria, comprobante_url)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *
        """
        return await self.execute(query, tuple(expense_data.values()))

    async def get_expenses(self, project_id: UUID) -> List[dict]:
        """Get all expenses for a project"""
        query = """
        SELECT * FROM project_expenses 
        WHERE project_id = %s AND aprobado = true
        ORDER BY fecha DESC
        """
        return await self.fetch_all(query, (str(project_id),))

    async def get_expense_by_id(self, expense_id: UUID) -> Optional[dict]:
        """Get expense by ID"""
        query = "SELECT * FROM project_expenses WHERE id = %s"
        return await self.fetch_one(query, (str(expense_id),))

    async def approve_expense(self, expense_id: UUID) -> Optional[dict]:
        """Approve project expense"""
        query = "UPDATE project_expenses SET aprobado = true WHERE id = %s RETURNING *"
        return await self.execute(query, (str(expense_id),))

    async def calculate_progress(self, project_id: UUID) -> int:
        """Calculate project progress percentage"""
        query = "SELECT progreso FROM proyectos WHERE id = %s"
        result = await self.fetch_one(query, (str(project_id),))
        return result["progreso"] if result else 0

    async def update_progress(self, project_id: UUID, progress: int) -> Optional[dict]:
        """Update project progress"""
        query = "UPDATE proyectos SET progreso = %s, updated_at = now() WHERE id = %s RETURNING *"
        return await self.execute(query, (progress, str(project_id)))
