#!/usr/bin/env python3
"""
Script para ejecutar las migraciones de la Fase 9: Integraciones Avanzadas
Ejecuta todas las migraciones SQL necesarias para webhooks, API pública, OAuth y banking
"""

import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(backend_dir))

def run_migration(migration_file: str, description: str):
    """Run a single migration file"""
    print(f"\n🔄 Ejecutando migración: {description}")
    print(f"📄 Archivo: {migration_file}")

    migration_path = backend_dir / migration_file

    if not migration_path.exists():
        print(f"❌ Error: Archivo de migración no encontrado: {migration_path}")
        return False

    # Read migration content
    with open(migration_path, 'r', encoding='utf-8') as f:
        migration_sql = f.read()

    print("📋 Contenido de la migración:")
    print("=" * 50)
    print(migration_sql[:500] + "..." if len(migration_sql) > 500 else migration_sql)
    print("=" * 50)

    print("✅ Migración lista para ejecutar en Supabase SQL Editor"    print(f"💡 Copia y pega el contenido del archivo en: {migration_path}")
    return True

def main():
    """Main migration execution"""
    print("🚀 Migraciones de la Fase 9: Integraciones Avanzadas")
    print("=" * 60)

    migrations = [
        ("migration_phase9_webhooks.sql", "Webhooks - Sistema de notificaciones externas"),
        ("migration_phase9_public_api.sql", "API Pública - Acceso limitado con rate limiting"),
        ("migration_phase9_oauth.sql", "OAuth2/SSO - Autenticación externa"),
        ("migration_phase9_banking.sql", "Banking - Integración con sistemas financieros")
    ]

    success_count = 0

    for migration_file, description in migrations:
        if run_migration(migration_file, description):
            success_count += 1

    print(f"\n📊 Resumen de migraciones: {success_count}/{len(migrations)} listas")
    print("\n📝 Instrucciones:")
    print("1. Ve al dashboard de Supabase")
    print("2. Abre el SQL Editor")
    print("3. Copia y pega cada migración SQL")
    print("4. Ejecuta cada una en orden")
    print("5. Verifica que no haya errores")

    print("\n🎯 Después de ejecutar las migraciones:")
    print("- Las nuevas APIs estarán disponibles")
    print("- Podrás configurar OAuth providers")
    print("- Los webhooks estarán listos para recibir eventos")
    print("- La API pública tendrá rate limiting")

    if success_count == len(migrations):
        print("\n✅ Todas las migraciones de la Fase 9 están preparadas!")
    else:
        print(f"\n⚠️  {len(migrations) - success_count} migraciones con problemas")

if __name__ == "__main__":
    main()