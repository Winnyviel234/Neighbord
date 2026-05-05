import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError, ConnectionError
from app.core.config import settings
from .model import IndexDocument, SearchQuery, SearchResult, SearchStats

logger = logging.getLogger(__name__)

class ElasticsearchRepository:
    def __init__(self):
        self.enabled = False
        self.client: Optional[AsyncElasticsearch] = None
        self.index_name = "neighbord_documents"
        self._initialize_elasticsearch()

    def _initialize_elasticsearch(self):
        """Initialize Elasticsearch connection"""
        try:
            if settings.elasticsearch_url:
                self.client = AsyncElasticsearch([settings.elasticsearch_url])
                self.enabled = True
                logger.info("Elasticsearch search enabled")
            else:
                logger.warning("Elasticsearch URL not configured, search disabled")
                self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch: {e}")
            self.enabled = False

    async def health_check(self) -> bool:
        """Check if Elasticsearch is healthy"""
        if not self.enabled or not self.client:
            return False

        try:
            response = await self.client.cluster.health()
            return response["status"] in ["green", "yellow"]
        except Exception as e:
            logger.error(f"Elasticsearch health check failed: {e}")
            return False

    async def create_index_if_not_exists(self):
        """Create index with proper mappings if it doesn't exist"""
        if not self.enabled or not self.client:
            return

        try:
            # Check if index exists
            exists = await self.client.indices.exists(index=self.index_name)
            if exists:
                return

            # Create index with mappings
            mappings = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "type": {"type": "keyword"},
                        "title": {"type": "text", "analyzer": "spanish"},
                        "content": {"type": "text", "analyzer": "spanish"},
                        "metadata": {"type": "object"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"}
                    }
                },
                "settings": {
                    "analysis": {
                        "analyzer": {
                            "spanish": {
                                "type": "standard",
                                "stopwords": "_spanish_"
                            }
                        }
                    }
                }
            }

            await self.client.indices.create(
                index=self.index_name,
                body=mappings
            )
            logger.info(f"Created Elasticsearch index: {self.index_name}")

        except Exception as e:
            logger.error(f"Failed to create index: {e}")

    async def index_document(self, document: IndexDocument) -> bool:
        """Index a document for search"""
        if not self.enabled or not self.client:
            return False

        try:
            doc_body = {
                "id": document.id,
                "type": document.type,
                "title": document.title,
                "content": document.content,
                "metadata": document.metadata,
                "created_at": document.created_at.isoformat() if document.created_at else None,
                "updated_at": document.updated_at.isoformat() if document.updated_at else None
            }

            await self.client.index(
                index=self.index_name,
                id=document.id,
                document=doc_body
            )
            return True

        except Exception as e:
            logger.error(f"Failed to index document {document.id}: {e}")
            return False

    async def update_document(self, document_id: str, updates: Dict[str, Any]) -> bool:
        """Update an indexed document"""
        if not self.enabled or not self.client:
            return False

        try:
            await self.client.update(
                index=self.index_name,
                id=document_id,
                doc=updates
            )
            return True

        except NotFoundError:
            logger.warning(f"Document {document_id} not found for update")
            return False
        except Exception as e:
            logger.error(f"Failed to update document {document_id}: {e}")
            return False

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from index"""
        if not self.enabled or not self.client:
            return False

        try:
            await self.client.delete(
                index=self.index_name,
                id=document_id
            )
            return True

        except NotFoundError:
            logger.warning(f"Document {document_id} not found for deletion")
            return False
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False

    async def search(self, search_query: SearchQuery) -> Dict[str, Any]:
        """Perform search query"""
        if not self.enabled or not self.client:
            return {"total": 0, "results": [], "took_ms": 0}

        try:
            # Build query
            query_body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": search_query.query,
                                    "fields": ["title^3", "content^2", "metadata.*"],
                                    "fuzziness": "AUTO"
                                }
                            }
                        ],
                        "filter": []
                    }
                },
                "highlight": {
                    "fields": {
                        "title": {},
                        "content": {}
                    }
                },
                "size": search_query.limit,
                "from": search_query.offset
            }

            # Add filters
            if search_query.filters:
                for field, value in search_query.filters.items():
                    if isinstance(value, list):
                        query_body["query"]["bool"]["filter"].append({
                            "terms": {field: value}
                        })
                    else:
                        query_body["query"]["bool"]["filter"].append({
                            "term": {field: value}
                        })

            # Add sorting
            if search_query.sort_by:
                query_body["sort"] = [
                    {
                        search_query.sort_by: {
                            "order": search_query.sort_order
                        }
                    }
                ]

            # Execute search
            start_time = datetime.now()
            response = await self.client.search(
                index=self.index_name,
                body=query_body
            )
            took_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Process results
            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                highlights = []
                if "highlight" in hit:
                    for field_highlights in hit["highlight"].values():
                        highlights.extend(field_highlights)

                result = SearchResult(
                    id=source["id"],
                    type=source["type"],
                    title=source["title"],
                    content=source["content"],
                    metadata=source["metadata"],
                    score=hit["_score"],
                    highlights=highlights,
                    created_at=datetime.fromisoformat(source["created_at"]) if source.get("created_at") else None,
                    updated_at=datetime.fromisoformat(source["updated_at"]) if source.get("updated_at") else None
                )
                results.append(result)

            return {
                "total": response["hits"]["total"]["value"],
                "results": results,
                "took_ms": int(took_ms),
                "facets": None  # Could be implemented later
            }

        except Exception as e:
            logger.error(f"Search query failed: {e}")
            return {"total": 0, "results": [], "took_ms": 0}

    async def get_stats(self) -> SearchStats:
        """Get search statistics"""
        if not self.enabled or not self.client:
            return SearchStats(
                total_documents=0,
                index_size_bytes=0,
                search_requests_total=0,
                avg_response_time_ms=0.0
            )

        try:
            # Get index stats
            stats_response = await self.client.indices.stats(index=self.index_name)
            index_stats = stats_response["indices"].get(self.index_name, {})

            total_docs = index_stats.get("total", {}).get("docs", {}).get("count", 0)
            index_size = index_stats.get("total", {}).get("store", {}).get("size_in_bytes", 0)

            # For now, return basic stats
            # Could be enhanced with actual search metrics
            return SearchStats(
                total_documents=total_docs,
                index_size_bytes=index_size,
                search_requests_total=0,  # Would need separate tracking
                avg_response_time_ms=0.0,  # Would need separate tracking
                last_updated=datetime.now()
            )

        except Exception as e:
            logger.error(f"Failed to get search stats: {e}")
            return SearchStats(
                total_documents=0,
                index_size_bytes=0,
                search_requests_total=0,
                avg_response_time_ms=0.0
            )

# Global search repository instance
search_repository = ElasticsearchRepository()