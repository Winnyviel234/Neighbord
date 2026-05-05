from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List
from app.core.security import get_current_user, require_permissions
from .service import ProjectService
from .repository import ProjectRepository
from .model import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])


async def get_project_service() -> ProjectService:
    """Dependency injection for project service"""
    repository = ProjectRepository()
    return ProjectService(repository)


@router.get("", response_model=List[ProjectResponse])
async def get_projects(
    sector_id: UUID = None,
    status: str = None,
    current_user: dict = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    """Get all projects with optional filtering"""
    return await service.get_projects(sector_id, status)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: dict = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
    _ = Depends(require_permissions(["manage_projects", "admin"]))
):
    """Create new project"""
    return await service.create_project(project, current_user["id"])


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    """Get project by ID"""
    try:
        return await service.get_project(project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
    _ = Depends(require_permissions(["manage_projects", "admin"]))
):
    """Update project"""
    try:
        return await service.update_project(project_id, project_update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
    _ = Depends(require_permissions(["manage_projects", "admin"]))
):
    """Delete project (soft delete)"""
    await service.delete_project(project_id)


@router.get("/sector/{sector_id}", response_model=List[ProjectResponse])
async def get_sector_projects(
    sector_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    """Get all projects in a sector"""
    return await service.get_sector_projects(sector_id)


@router.get("/my/projects", response_model=List[ProjectResponse])
async def get_my_projects(
    current_user: dict = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    """Get projects managed by current user"""
    return await service.get_responsible_projects(current_user["id"])


@router.post("/{project_id}/expenses", status_code=status.HTTP_201_CREATED)
async def register_expense(
    project_id: UUID,
    expense_data: dict,
    current_user: dict = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
    _ = Depends(require_permissions(["manage_projects", "admin"]))
):
    """Register expense for project"""
    try:
        return await service.register_expense(project_id, expense_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{project_id}/expenses")
async def get_expenses(
    project_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    """Get approved expenses for project"""
    try:
        return await service.get_project_expenses(project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{project_id}/progress")
async def update_progress(
    project_id: UUID,
    progress: int,
    current_user: dict = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
    _ = Depends(require_permissions(["manage_projects", "admin"]))
):
    """Update project progress"""
    try:
        return await service.update_progress(project_id, progress)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/budget-summary")
async def get_budget_summary(
    project_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    """Get budget summary for project"""
    try:
        return await service.get_budget_summary(project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/expenses/{expense_id}/approve", status_code=status.HTTP_200_OK)
async def approve_expense(
    expense_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
    _ = Depends(require_permissions(["manage_finances", "admin"]))
):
    """Approve project expense (tesorero only)"""
    try:
        return await service.approve_expense(expense_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
