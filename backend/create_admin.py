#!/usr/bin/env python3
"""Create admin user from .env credentials"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.security import hash_password
from app.core.supabase import table

async def create_admin_user():
    """Create admin user with credentials from .env"""
    try:
        print("🔑 Creating admin user from .env credentials...")
        print(f"   Email: {settings.admin_email}")
        
        # Check if admin user already exists
        try:
            existing = table("usuarios").select("*").eq("email", settings.admin_email).execute()
        except Exception:
            existing = None
        
        if existing and existing.data and len(existing.data) > 0:
            print(f"✅ Admin user already exists!")
            data = existing.data[0]
            print(f"   Email: {data.get('email')}")
            print(f"   Role: {data.get('rol')}")
            print(f"   Status: {data.get('estado')}")
            return
        
        # Create admin user
        user_data = {
            "nombre": settings.admin_name,
            "email": settings.admin_email,
            "password_hash": hash_password(settings.admin_password),
            "telefono": "555-0000",
            "direccion": "Admin Address",
            "estado": "aprobado",
            "rol": "admin",
            "activo": True
        }
        
        print(f"📝 Inserting admin user...")
        result = table("usuarios").insert(user_data).execute()
        
        if result.data:
            print(f"✅ Admin user created successfully!")
            print(f"   ID: {result.data[0].get('id')}")
            print(f"   Email: {result.data[0].get('email')}")
            print(f"   Role: {result.data[0].get('rol')}")
            print(f"\n🔐 You can now login with:")
            print(f"   Email: {settings.admin_email}")
            print(f"   Password: {settings.admin_password}")
        else:
            print(f"❌ Failed to create admin user")
            print(f"   Response: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_admin_user())
