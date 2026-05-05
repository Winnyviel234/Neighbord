from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List
from app.core.security import get_current_user, require_permissions
from .service import DirectivaService
from .repository import DirectivaRepository
from .model import (
    CargoCreate, CargoUpdate, CargoAsignacion, CargoAsignacionUpdate,
    CargoResponse, CargoAsignacionResponse, DirectivaResponse
)

router = APIRouter(prefix="/directiva", tags=["Directiva"])


async def get_directiva_service() -> DirectivaService:
    """Dependency injection for directiva service"""
    repository = DirectivaRepository()
    return DirectivaService(repository)


# Cargo Management Endpoints
@router.get("/cargos", response_model=List[CargoResponse])
async def get_cargos(
    sector_id: UUID = None,
    current_user: dict = Depends(get_current_user),
    service: DirectivaService = Depends(get_directiva_service)
):
    """Get all cargos (filtered by sector if provided)"""
    if sector_id:
        return await service.get_sector_cargos(sector_id)
    # Return all if admin
    try:
        await service.get_sector_cargos(sector_id) if sector_id else []
    except:
        raise HTTPException(status_code=403, detail="Must specify sector_id")


@router.post("/cargos", response_model=CargoResponse, status_code=status.HTTP_201_CREATED)
async def create_cargo(
    cargo: CargoCreate,
    current_user: dict = Depends(get_current_user),
    service: DirectivaService = Depends(get_directiva_service),
    _ = Depends(require_permissions(["manage_directiva", "admin"]))
):
    """Create new cargo position"""
    return await service.create_cargo(cargo)


@router.get("/cargos/{cargo_id}", response_model=CargoResponse)
async def get_cargo(
    cargo_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: DirectivaService = Depends(get_directiva_service)
):
    """Get cargo by ID"""
    try:
        return await service.get_cargo(cargo_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/cargos/{cargo_id}", response_model=CargoResponse)
async def update_cargo(
    cargo_id: UUID,
    cargo_update: CargoUpdate,
    current_user: dict = Depends(get_current_user),
    service: DirectivaService = Depends(get_directiva_service),
    _ = Depends(require_permissions(["manage_directiva", "admin"]))
):
    """Update cargo"""
    try:
        return await service.update_cargo(cargo_id, cargo_update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/cargos/{cargo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cargo(
    cargo_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: DirectivaService = Depends(get_directiva_service),
    _ = Depends(require_permissions(["manage_directiva", "admin"]))
):
    """Delete cargo"""
    await service.delete_cargo(cargo_id)


# Assignment Management Endpoints
@router.post("/asignaciones", response_model=CargoAsignacionResponse, status_code=status.HTTP_201_CREATED)
async def assign_cargo(
    asignacion: CargoAsignacion,
    current_user: dict = Depends(get_current_user),
    service: DirectivaService = Depends(get_directiva_service),
    _ = Depends(require_permissions(["manage_directiva", "admin"]))
):
    """Assign user to cargo position"""
    try:
        return await service.assign_cargo(asignacion)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/asignaciones", response_model=List[dict])
async def get_active_assignments(
    sector_id: UUID = None,
    current_user: dict = Depends(get_current_user),
    service: DirectivaService = Depends(get_directiva_service)
):
    """Get all active assignments"""
    return await service.get_active_assignments(sector_id)


@router.get("/asignaciones/user/{user_id}", response_model=List[dict])
async def get_user_assignments(
    user_id: UUID,
    sector_id: UUID = None,
    current_user: dict = Depends(get_current_user),
    service: DirectivaService = Depends(get_directiva_service)
):
    """Get all assignments for a user"""
    return await service.get_user_assignments(user_id, sector_id)


@router.get("/asignaciones/{asignacion_id}", response_model=CargoAsignacionResponse)
async def get_assignment(
    asignacion_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: DirectivaService = Depends(get_directiva_service)
):
    """Get assignment by ID"""
    try:
        return await service.get_assignment(asignacion_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/asignaciones/{asignacion_id}", response_model=CargoAsignacionResponse)
async def update_assignment(
    asignacion_id: UUID,
    update: CargoAsignacionUpdate,
    current_user: dict = Depends(get_current_user),
    service: DirectivaService = Depends(get_directiva_service),
    _ = Depends(require_permissions(["manage_directiva", "admin"]))
):
    """Update assignment"""
    try:
        return await service.update_assignment(asignacion_id, update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/asignaciones/{asignacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def terminate_assignment(
    asignacion_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: DirectivaService = Depends(get_directiva_service),
    _ = Depends(require_permissions(["manage_directiva", "admin"]))
):
    """Terminate assignment"""
    try:
        await service.terminate_assignment(asignacion_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Directiva Structure Endpoints
@router.get("/sector/{sector_id}", response_model=DirectivaResponse)
async def get_sector_directiva(
    sector_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: DirectivaService = Depends(get_directiva_service)
):
    """Get complete directiva structure for a sector"""
    return await service.get_directiva(sector_id)


@router.get("/sector/{sector_id}/stats")
async def get_directiva_stats(
    sector_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: DirectivaService = Depends(get_directiva_service)
):
    """Get directiva statistics"""
    return await service.get_directiva_stats(sector_id)


@router.post("/sector/{sector_id}/initialize", response_model=List[CargoResponse])
async def initialize_directiva(
    sector_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: DirectivaService = Depends(get_directiva_service),
    _ = Depends(require_permissions(["admin"]))
):
    """Initialize default cargos for new sector"""
    return await service.initialize_sector_directiva(sector_id)
