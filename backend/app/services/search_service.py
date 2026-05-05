import requests
from app.core.config import settings


class SearchService:
    def __init__(self):
        self.url = settings.elasticsearch_url.strip()
        self.enabled = bool(self.url)

    def search_global(self, query: str, index: str | None = None, size: int = 20) -> dict:
        if not self.enabled:
            return {"error": "Elasticsearch no está configurado."}

        target = index.strip() if index else "_all"
        url = f"{self.url.rstrip('/')}/{target}/_search"
        payload = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["*"],
                }
            },
            "size": size,
        }

        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        response.raise_for_status()
        payload = response.json()
        hits = payload.get("hits", {}).get("hits", [])

        return {
            "total": payload.get("hits", {}).get("total", {}),
            "results": [
                {
                    "index": hit.get("_index"),
                    "id": hit.get("_id"),
                    "score": hit.get("_score"),
                    "source": hit.get("_source"),
                }
                for hit in hits
            ],
        }
