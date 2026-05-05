#!/usr/bin/env python3
"""
Script de inicialización para servicios de optimización
Configura Redis y Elasticsearch si están disponibles
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.cache.redis_cache import cache_manager
from app.modules.search.service import SearchService

async def initialize_services():
    """Initialize optimization services"""
    print("🚀 Inicializando servicios de optimización...")

    # Check Redis
    print("\n📊 Verificando Redis...")
    if settings.redis_url:
        redis_healthy = await cache_manager.health_check()
        if redis_healthy:
            print("✅ Redis conectado y funcionando")
        else:
            print("❌ Redis configurado pero no disponible")
    else:
        print("⚠️  Redis no configurado (usando cache en memoria)")

    # Check Elasticsearch
    print("\n🔍 Verificando Elasticsearch...")
    search_service = SearchService()
    if search_service.repo.enabled:
        es_healthy = await search_service.health_check()
        if es_healthy:
            print("✅ Elasticsearch conectado y funcionando")

            # Initialize search index
            index_created = await search_service.initialize_search_index()
            if index_created:
                print("✅ Índice de búsqueda creado/inicializado")
            else:
                print("❌ Error al crear índice de búsqueda")
        else:
            print("❌ Elasticsearch configurado pero no disponible")
    else:
        print("⚠️  Elasticsearch no configurado (búsqueda básica disponible)")

    # Summary
    print("\n📋 Resumen de servicios:")
    print(f"   Cache Redis: {'✅' if cache_manager.enabled and await cache_manager.health_check() else '❌'}")
    print(f"   Elasticsearch: {'✅' if search_service.repo.enabled and await search_service.health_check() else '❌'}")

    print("\n🎯 Servicios de optimización inicializados!")

if __name__ == "__main__":
    asyncio.run(initialize_services())