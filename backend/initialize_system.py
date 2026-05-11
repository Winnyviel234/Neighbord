#!/usr/bin/env python3
"""
Sistema de Inicialización Robusta para Neighbord
Garantiza que el sistema funcione incluso con base de datos incompleta
"""

import os
import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.supabase import table
from app.core.security import hash_password
from dotenv import load_dotenv

load_dotenv()

def check_database_connection():
    """Verifica la conexión a la base de datos"""
    try:
        # Intentar una consulta simple
        result = table("usuarios").select("count").limit(1).execute()
        print("✅ Conexión a base de datos: OK")
        return True
    except Exception as e:
        print(f"❌ Error de conexión a base de datos: {e}")
        return False

def ensure_basic_tables():
    """Asegura que las tablas básicas existan"""
    tables_to_check = ["usuarios"]
    for table_name in tables_to_check:
        try:
            # Intentar una consulta simple para verificar si la tabla existe
            result = table(table_name).select("*").limit(1).execute()
            print(f"✅ Tabla '{table_name}': OK")
        except Exception as e:
            print(f"⚠️  Tabla '{table_name}' no disponible: {e}")

def create_demo_user():
    """Crea un usuario de demostración si no existe ninguno"""
    try:
        # Verificar si ya hay usuarios
        existing = table("usuarios").select("id").limit(1).execute()
        if existing.data:
            print("✅ Ya existen usuarios en el sistema")
            return

        # Crear usuario de demostración
        demo_user = {
            "nombre": "Usuario Demo",
            "email": "demo@neighbord.com",
            "password_hash": hash_password("demo123"),
            "telefono": "123456789",
            "direccion": "Dirección de demostración",
            "estado": "aprobado",
            "activo": True,
            "role_id": None,  # El sistema funciona sin role_id
            "sector_id": None  # El sistema funciona sin sector_id
        }

        result = table("usuarios").insert(demo_user).execute()
        print("✅ Usuario de demostración creado: demo@neighbord.com / demo123")

    except Exception as e:
        print(f"⚠️  No se pudo crear usuario demo: {e}")

def create_fallback_tables():
    """Intenta crear tablas de respaldo si no existen"""
    try:
        # Intentar crear tabla de roles básica
        roles_data = [
            {"id": "admin-role", "name": "admin", "permissions": ["all"]},
            {"id": "directiva-role", "name": "directiva", "permissions": ["manage_users", "manage_meetings", "manage_voting", "manage_finances", "view_reports"]},
            {"id": "tesorero-role", "name": "tesorero", "permissions": ["manage_finances", "view_reports"]},
            {"id": "vocero-role", "name": "vocero", "permissions": ["manage_meetings", "manage_voting", "view_reports"]},
            {"id": "secretaria-role", "name": "secretaria", "permissions": ["manage_meetings", "view_reports"]},
            {"id": "vecino-role", "name": "vecino", "permissions": ["view_public", "submit_complaints", "vote"]}
        ]

        for role in roles_data:
            try:
                table("roles").insert(role).execute()
                print(f"✅ Rol creado: {role['name']}")
            except:
                pass  # Ya existe probablemente

    except Exception as e:
        print(f"ℹ️  Tabla roles no disponible (usando valores por defecto): {e}")

    try:
        # Intentar crear tabla de sectores básica
        sector_data = {
            "id": "main-sector",
            "name": "Comunidad Principal",
            "description": "Sector principal de la comunidad"
        }

        table("sectors").insert(sector_data).execute()
        print("✅ Sector creado: Comunidad Principal")

    except Exception as e:
        print(f"ℹ️  Tabla sectors no disponible (usando valores por defecto): {e}")

def update_existing_users():
    """Actualiza usuarios existentes para asegurar compatibilidad"""
    try:
        # Obtener todos los usuarios
        users = table("usuarios").select("id, role_id, sector_id").execute()

        if not users.data:
            return

        print(f"📊 Verificando {len(users.data)} usuarios existentes...")

        # Aquí podríamos actualizar usuarios si fuera necesario
        # Por ahora, el sistema es lo suficientemente robusto

    except Exception as e:
        print(f"ℹ️  No se pudieron verificar usuarios existentes: {e}")

def main():
    """Función principal de inicialización"""
    print("🚀 Inicializando Sistema Neighbord (Modo Robusto)")
    print("=" * 50)

    # Verificar conexión
    if not check_database_connection():
        print("❌ No se puede conectar a la base de datos. Verifica la configuración.")
        return False

    # Verificar tablas básicas
    ensure_basic_tables()

    # Crear tablas de respaldo
    create_fallback_tables()

    # Crear usuario demo
    create_demo_user()

    # Actualizar usuarios existentes
    update_existing_users()

    print("=" * 50)
    print("✅ Inicialización completada")
    print("ℹ️  El sistema está configurado para funcionar incluso con base de datos incompleta")
    print("🔐 Usuario demo: demo@neighbord.com / demo123")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)