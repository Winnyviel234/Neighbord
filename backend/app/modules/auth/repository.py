from typing import Optional, Dict, Any
from uuid import UUID
from app.core.supabase import table
from app.modules.base import BaseRepository

# Hardcoded roles for reliability - no database dependency
DEFAULT_ROLES = {
    "admin": {
        "name": "admin",
        "permissions": ["all"]
    },
    "directiva": {
        "name": "directiva",
        "permissions": ["manage_users", "manage_meetings", "manage_voting", "manage_finances", "view_reports"]
    },
    "tesorero": {
        "name": "tesorero",
        "permissions": ["manage_finances", "view_reports"]
    },
    "vocero": {
        "name": "vocero",
        "permissions": ["manage_meetings", "manage_voting", "view_reports"]
    },
    "secretaria": {
        "name": "secretaria",
        "permissions": ["manage_meetings", "view_reports"]
    },
    "vecino": {
        "name": "vecino",
        "permissions": ["view_public", "submit_complaints", "vote"]
    }
}

DEFAULT_SECTOR = {
    "name": "Comunidad Principal",
    "description": "Sector principal de la comunidad"
}

class AuthRepository(BaseRepository):
    def __init__(self):
        pass

    def _table(self):
        return table("usuarios")

    def _get_role_info(self, role_name: str = "vecino") -> Dict[str, Any]:
        """Get role information with fallback to hardcoded defaults"""
        return DEFAULT_ROLES.get(role_name, DEFAULT_ROLES["vecino"])

    def _get_sector_info(self) -> Dict[str, Any]:
        """Get sector information with fallback"""
        return DEFAULT_SECTOR

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email with role information - robust version"""
        try:
            # Get user data first
            user_result = self._table().select("*").eq("email", email).single().execute()
            if not user_result.data:
                return None

            user = user_result.data

            # Try to get role info from database, fallback to hardcoded
            role_name = "vecino"  # Default fallback
            role_permissions = DEFAULT_ROLES["vecino"]["permissions"]

            try:
                if user.get("role_id"):
                    role_result = table("roles").select("name, permissions").eq("id", user["role_id"]).single().execute()
                    if role_result.data:
                        role_name = role_result.data.get("name", "vecino")
                        role_permissions = role_result.data.get("permissions", DEFAULT_ROLES["vecino"]["permissions"])
            except:
                # Database role lookup failed, use defaults
                pass

            # Try to get sector info, fallback to default
            sector_name = DEFAULT_SECTOR["name"]
            try:
                if user.get("sector_id"):
                    sector_result = table("sectors").select("name").eq("id", user["sector_id"]).single().execute()
                    if sector_result.data:
                        sector_name = sector_result.data.get("name", DEFAULT_SECTOR["name"])
            except:
                # Database sector lookup failed, use default
                pass

            # Add computed fields
            user["role_name"] = role_name
            user["role_permissions"] = role_permissions
            user["sector_name"] = sector_name

            return user

        except Exception as e:
            print(f"AuthRepository.get_by_email error: {e}")
            return None

    async def get_by_id(self, id: UUID) -> Optional[Dict[str, Any]]:
        """Get user by ID with role and sector - robust version"""
        try:
            # Get user data first
            user_result = self._table().select("*").eq("id", str(id)).single().execute()
            if not user_result.data:
                return None

            user = user_result.data

            # Try to get role info from database, fallback to hardcoded
            role_name = "vecino"  # Default fallback
            role_permissions = DEFAULT_ROLES["vecino"]["permissions"]

            try:
                if user.get("role_id"):
                    role_result = table("roles").select("name, permissions").eq("id", user["role_id"]).single().execute()
                    if role_result.data:
                        role_name = role_result.data.get("name", "vecino")
                        role_permissions = role_result.data.get("permissions", DEFAULT_ROLES["vecino"]["permissions"])
            except:
                # Database role lookup failed, use defaults
                pass

            # Try to get sector info, fallback to default
            sector_name = DEFAULT_SECTOR["name"]
            try:
                if user.get("sector_id"):
                    sector_result = table("sectors").select("name").eq("id", user["sector_id"]).single().execute()
                    if sector_result.data:
                        sector_name = sector_result.data.get("name", DEFAULT_SECTOR["name"])
            except:
                # Database sector lookup failed, use default
                pass

            # Add computed fields
            user["role_name"] = role_name
            user["role_permissions"] = role_permissions
            user["sector_name"] = sector_name

            return user

        except Exception as e:
            print(f"AuthRepository.get_by_id error: {e}")
            return None
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user - robust version with fallbacks"""
        try:
            data["rol"] = data.get("rol") or "vecino"

            sector_id = data.get("sector_id")
            if sector_id:
                try:
                    UUID(str(sector_id))
                except ValueError:
                    sector = table("sectors").select("id").eq("name", str(sector_id)).single().execute().data
                    if sector:
                        data["sector_id"] = sector["id"]
                    else:
                        data.pop("sector_id", None)

            # Try to set sector_id from database, fallback to None
            if not data.get("sector_id"):
                try:
                    sector_result = table("sectors").select("id").limit(1).execute()
                    if sector_result.data:
                        data["sector_id"] = sector_result.data[0]["id"]
                except:
                    # Sectors table doesn't exist or query failed
                    pass

            result = self._table().insert(data).execute()
            user = result.data[0]
            user["role_name"] = user.get("rol", "vecino")
            user["role_permissions"] = DEFAULT_ROLES.get(user["role_name"], DEFAULT_ROLES["vecino"])["permissions"]
            return user

        except Exception as e:
            print(f"AuthRepository.create error: {e}")
            raise
    
    async def update(self, id: UUID, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user"""
        result = self._table().update(data).eq("id", str(id)).execute()
        return result.data[0] if result.data else None
    
    async def get_all(self, filters: Dict[str, Any] = None) -> list:
        """Not implemented for auth"""
        raise NotImplementedError
    
    async def delete(self, id: UUID) -> bool:
        """Not implemented for auth"""
        raise NotImplementedError
