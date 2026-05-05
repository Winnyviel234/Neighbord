from typing import List, Optional
from uuid import UUID
from .repository import ProjectRepository
from .model import ProjectCreate, ProjectUpdate, ProjectResponse


class ProjectService:
    """Service layer for project business logic"""

    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    async def create_project(self, project: ProjectCreate, user_id: UUID) -> ProjectResponse:
        """Create new project"""
        result = await self.repository.create(project, user_id)
        if not result:
            raise ValueError("Failed to create project")
        return ProjectResponse(**result)

    async def get_project(self, project_id: UUID) -> ProjectResponse:
        """Get project by ID"""
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        return ProjectResponse(**project)

    async def get_projects(self, sector_id: Optional[UUID] = None, status: Optional[str] = None) -> List[ProjectResponse]:
        """Get projects with optional filtering"""
        projects = await self.repository.get_all(sector_id, status)
        return [ProjectResponse(**p) for p in projects]

    async def update_project(self, project_id: UUID, project: ProjectUpdate) -> ProjectResponse:
        """Update project"""
        result = await self.repository.update(project_id, project)
        if not result:
            raise ValueError(f"Project {project_id} not found")
        return ProjectResponse(**result)

    async def delete_project(self, project_id: UUID) -> bool:
        """Delete project (soft delete)"""
        return await self.repository.delete(project_id)

    async def get_sector_projects(self, sector_id: UUID) -> List[ProjectResponse]:
        """Get all projects in a sector"""
        projects = await self.repository.get_by_sector(sector_id)
        return [ProjectResponse(**p) for p in projects]

    async def get_responsible_projects(self, user_id: UUID) -> List[ProjectResponse]:
        """Get projects managed by user"""
        projects = await self.repository.get_by_responsible(user_id)
        return [ProjectResponse(**p) for p in projects]

    async def register_expense(self, project_id: UUID, expense_data: dict) -> dict:
        """Register project expense"""
        # Validate project exists
        await self.get_project(project_id)
        
        expense_data["project_id"] = str(project_id)
        return await self.repository.add_expense(expense_data)

    async def get_project_expenses(self, project_id: UUID) -> List[dict]:
        """Get all approved expenses for project"""
        await self.get_project(project_id)
        return await self.repository.get_expenses(project_id)

    async def approve_expense(self, expense_id: UUID) -> dict:
        """Approve expense (tesorero only)"""
        expense = await self.repository.get_expense_by_id(expense_id)
        if not expense:
            raise ValueError(f"Expense {expense_id} not found")
        
        result = await self.repository.approve_expense(expense_id)
        return result

    async def update_progress(self, project_id: UUID, progress: int) -> ProjectResponse:
        """Update project progress percentage"""
        if not 0 <= progress <= 100:
            raise ValueError("Progress must be between 0 and 100")
        
        result = await self.repository.update_progress(project_id, progress)
        if not result:
            raise ValueError(f"Project {project_id} not found")
        return ProjectResponse(**result)

    async def get_budget_summary(self, project_id: UUID) -> dict:
        """Get budget summary for project"""
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        expenses = await self.repository.get_expenses(project_id)
        total_executed = sum(e["monto"] for e in expenses)
        
        return {
            "presupuesto_estimado": project["presupuesto_estimado"],
            "presupuesto_aprobado": project["presupuesto_aprobado"],
            "presupuesto_ejecutado": total_executed,
            "sobrante": (project["presupuesto_aprobado"] or project["presupuesto_estimado"]) - total_executed,
            "porcentaje_ejecucion": (total_executed / (project["presupuesto_aprobado"] or project["presupuesto_estimado"])) * 100
        }
