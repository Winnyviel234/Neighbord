import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from app.core.cache.decorators import cached, cache_invalidate_pattern
from .repository import search_repository
from .model import (
    SearchQuery, SearchResponse, IndexDocument, SearchStats,
    UserSearchFilters, ComplaintSearchFilters, MeetingSearchFilters, ProjectSearchFilters
)

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, repository=None):
        self.repo = repository or search_repository

    async def initialize_search_index(self) -> bool:
        """Initialize search index and mappings"""
        if not self.repo.enabled:
            logger.warning("Search is disabled - Elasticsearch not configured")
            return False

        try:
            await self.repo.create_index_if_not_exists()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize search index: {e}")
            return False

    @cached(ttl_seconds=300, key_prefix="search")
    async def search(self, query: str, filters: Optional[Dict[str, Any]] = None,
                    limit: int = 20, offset: int = 0) -> SearchResponse:
        """Perform search with caching"""
        if not self.repo.enabled:
            return SearchResponse(
                query=query,
                total=0,
                results=[],
                took_ms=0
            )

        search_query = SearchQuery(
            query=query,
            filters=filters or {},
            limit=limit,
            offset=offset
        )

        result = await self.repo.search(search_query)

        return SearchResponse(
            query=query,
            total=result["total"],
            results=result["results"],
            took_ms=result["took_ms"],
            facets=result.get("facets")
        )

    async def index_user(self, user_data: Dict[str, Any]) -> bool:
        """Index user for search"""
        if not self.repo.enabled:
            return False

        try:
            document = IndexDocument(
                id=str(user_data["id"]),
                type="user",
                title=f"{user_data.get('nombre', '')} {user_data.get('apellido', '')}".strip(),
                content=f"{user_data.get('email', '')} {user_data.get('telefono', '')} {user_data.get('direccion', '')}",
                metadata={
                    "email": user_data.get("email"),
                    "telefono": user_data.get("telefono"),
                    "sector_id": str(user_data.get("sector_id")) if user_data.get("sector_id") else None,
                    "role_name": user_data.get("role_name"),
                    "estado": user_data.get("estado")
                },
                created_at=user_data.get("created_at"),
                updated_at=user_data.get("updated_at")
            )

            success = await self.repo.index_document(document)
            if success:
                logger.debug(f"Indexed user {user_data['id']}")
            return success

        except Exception as e:
            logger.error(f"Failed to index user {user_data.get('id')}: {e}")
            return False

    async def index_complaint(self, complaint_data: Dict[str, Any]) -> bool:
        """Index complaint for search"""
        if not self.repo.enabled:
            return False

        try:
            document = IndexDocument(
                id=str(complaint_data["id"]),
                type="complaint",
                title=complaint_data.get("titulo", ""),
                content=complaint_data.get("descripcion", ""),
                metadata={
                    "estado": complaint_data.get("estado"),
                    "prioridad": complaint_data.get("prioridad"),
                    "sector_id": str(complaint_data.get("sector_id")) if complaint_data.get("sector_id") else None,
                    "user_id": str(complaint_data.get("user_id")) if complaint_data.get("user_id") else None,
                    "assigned_to": str(complaint_data.get("assigned_to")) if complaint_data.get("assigned_to") else None
                },
                created_at=complaint_data.get("created_at"),
                updated_at=complaint_data.get("updated_at")
            )

            success = await self.repo.index_document(document)
            if success:
                logger.debug(f"Indexed complaint {complaint_data['id']}")
            return success

        except Exception as e:
            logger.error(f"Failed to index complaint {complaint_data.get('id')}: {e}")
            return False

    async def index_meeting(self, meeting_data: Dict[str, Any]) -> bool:
        """Index meeting for search"""
        if not self.repo.enabled:
            return False

        try:
            document = IndexDocument(
                id=str(meeting_data["id"]),
                type="meeting",
                title=meeting_data.get("titulo", ""),
                content=meeting_data.get("descripcion", ""),
                metadata={
                    "tipo": meeting_data.get("tipo"),
                    "estado": meeting_data.get("estado"),
                    "sector_id": str(meeting_data.get("sector_id")) if meeting_data.get("sector_id") else None,
                    "fecha": meeting_data.get("fecha").isoformat() if meeting_data.get("fecha") else None,
                    "ubicacion": meeting_data.get("ubicacion")
                },
                created_at=meeting_data.get("created_at"),
                updated_at=meeting_data.get("updated_at")
            )

            success = await self.repo.index_document(document)
            if success:
                logger.debug(f"Indexed meeting {meeting_data['id']}")
            return success

        except Exception as e:
            logger.error(f"Failed to index meeting {meeting_data.get('id')}: {e}")
            return False

    async def index_project(self, project_data: Dict[str, Any]) -> bool:
        """Index project for search"""
        if not self.repo.enabled:
            return False

        try:
            document = IndexDocument(
                id=str(project_data["id"]),
                type="project",
                title=project_data.get("nombre", ""),
                content=project_data.get("descripcion", ""),
                metadata={
                    "estado": project_data.get("estado"),
                    "sector_id": str(project_data.get("sector_id")) if project_data.get("sector_id") else None,
                    "presupuesto": project_data.get("presupuesto"),
                    "fecha_inicio": project_data.get("fecha_inicio").isoformat() if project_data.get("fecha_inicio") else None,
                    "fecha_fin": project_data.get("fecha_fin").isoformat() if project_data.get("fecha_fin") else None
                },
                created_at=project_data.get("created_at"),
                updated_at=project_data.get("updated_at")
            )

            success = await self.repo.index_document(document)
            if success:
                logger.debug(f"Indexed project {project_data['id']}")
            return success

        except Exception as e:
            logger.error(f"Failed to index project {project_data.get('id')}: {e}")
            return False

    @cache_invalidate_pattern("search:*")
    async def update_document(self, document_id: str, updates: Dict[str, Any]) -> bool:
        """Update indexed document and invalidate cache"""
        if not self.repo.enabled:
            return False

        return await self.repo.update_document(document_id, updates)

    @cache_invalidate_pattern("search:*")
    async def delete_document(self, document_id: str) -> bool:
        """Delete document from index and invalidate cache"""
        if not self.repo.enabled:
            return False

        return await self.repo.delete_document(document_id)

    async def get_search_stats(self) -> SearchStats:
        """Get search statistics"""
        return await self.repo.get_stats()

    async def health_check(self) -> bool:
        """Check search service health"""
        if not self.repo.enabled:
            return False
        return await self.repo.health_check()

    # Specialized search methods
    async def search_users(self, query: str, filters: UserSearchFilters, limit: int = 20) -> SearchResponse:
        """Search users with specific filters"""
        search_filters = {}

        if filters.sector_id:
            search_filters["metadata.sector_id"] = filters.sector_id
        if filters.role:
            search_filters["metadata.role_name"] = filters.role
        if filters.status:
            search_filters["metadata.estado"] = filters.status
        if filters.date_range:
            # Could add date range filters here
            pass

        search_filters["type"] = "user"

        return await self.search(query, search_filters, limit)

    async def search_complaints(self, query: str, filters: ComplaintSearchFilters, limit: int = 20) -> SearchResponse:
        """Search complaints with specific filters"""
        search_filters = {}

        if filters.status:
            search_filters["metadata.estado"] = filters.status
        if filters.priority:
            search_filters["metadata.prioridad"] = filters.priority
        if filters.assigned_to:
            search_filters["metadata.assigned_to"] = filters.assigned_to
        if filters.sector_id:
            search_filters["metadata.sector_id"] = filters.sector_id

        search_filters["type"] = "complaint"

        return await self.search(query, search_filters, limit)

    async def search_meetings(self, query: str, filters: MeetingSearchFilters, limit: int = 20) -> SearchResponse:
        """Search meetings with specific filters"""
        search_filters = {}

        if filters.status:
            search_filters["metadata.estado"] = filters.status
        if filters.type:
            search_filters["metadata.tipo"] = filters.type
        if filters.sector_id:
            search_filters["metadata.sector_id"] = filters.sector_id

        search_filters["type"] = "meeting"

        return await self.search(query, search_filters, limit)

    async def search_projects(self, query: str, filters: ProjectSearchFilters, limit: int = 20) -> SearchResponse:
        """Search projects with specific filters"""
        search_filters = {}

        if filters.status:
            search_filters["metadata.estado"] = filters.status
        if filters.sector_id:
            search_filters["metadata.sector_id"] = filters.sector_id
        if filters.budget_min or filters.budget_max:
            # Could add range filters for budget
            pass

        search_filters["type"] = "project"

        return await self.search(query, search_filters, limit)