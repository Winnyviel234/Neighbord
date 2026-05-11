from typing import List
from uuid import UUID
from fastapi import HTTPException
from app.modules.roles.repository import RoleRepository

class RoleService:
    def __init__(self):
        self.repo = RoleRepository()

    async def get_roles(self) -> List[dict]:
        roles = await self.repo.get_all()
        return roles

    async def get_role(self, role_id: UUID) -> dict:
        role = await self.repo.get_by_id(role_id)
        if not role:
            raise HTTPException(404, "Rol no encontrado")
        return role

    async def create_role(self, data) -> dict:
        existing = await self.repo.get_by_name(data.name)
        if existing:
            raise HTTPException(409, "Ya existe un rol con ese nombre")
        role = await self.repo.create(data.model_dump())
        return role

    async def update_role(self, role_id: UUID, data) -> dict:
        existing = await self.repo.get_by_id(role_id)
        if not existing:
            raise HTTPException(404, "Rol no encontrado")

        if data.name:
            duplicate = await self.repo.get_by_name(data.name)
            if duplicate and str(duplicate["id"]) != str(role_id):
                raise HTTPException(409, "Ya existe un rol con ese nombre")

        updated = await self.repo.update(role_id, data.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(400, "No se pudo actualizar el rol")
        return updated

    async def delete_role(self, role_id: UUID) -> dict:
        role = await self.repo.get_by_id(role_id)
        if not role:
            raise HTTPException(404, "Rol no encontrado")
        if role.get("name") in ["admin", "directiva", "tesorero", "vocero", "secretaria", "vecino"]:
            raise HTTPException(400, "No se puede eliminar un rol base del sistema")
        success = await self.repo.delete(role_id)
        if not success:
            raise HTTPException(400, "No se pudo eliminar el rol")
        return {"message": "Rol eliminado correctamente"}
