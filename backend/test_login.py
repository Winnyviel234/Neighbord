#!/usr/bin/env python3
"""Test script to verify database connection and create test user"""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.security import hash_password
from app.core.supabase import table

async def test_database():
    """Test database connection and create test user"""
    try:
        print("📊 Connecting to Supabase...")
        
        # Test basic connection
        result = table("usuarios").select("*").limit(1).execute()
        print(f"✅ Database connected! Found {result.count} users total")
        
        # Check for admin user
        admin = table("usuarios").select("*").eq("email", "admin@test.com").maybe_single().execute()
        if admin.data:
            print(f"✅ Admin user exists: {admin.data.get('email')}")
        else:
            print("❌ Admin user not found, creating...")
            
            # Create test admin user
            user_data = {
                "nombre": "Admin Test",
                "email": "admin@test.com",
                "password_hash": hash_password("admin123"),
                "telefono": "555-0000",
                "direccion": "Test Address",
                "estado": "aprobado",
                "rol": "admin",
                "activo": True
            }
            
            insert_result = table("usuarios").insert(user_data).execute()
            if insert_result.data:
                print(f"✅ Created test admin: {insert_result.data[0].get('email')}")
            else:
                print("❌ Failed to create admin user")
        
        # Check for regular user
        user = table("usuarios").select("*").eq("email", "user@test.com").maybe_single().execute()
        if user.data:
            print(f"✅ Test user exists: {user.data.get('email')}")
        else:
            print("❌ Test user not found, creating...")
            
            # Create test regular user
            user_data = {
                "nombre": "User Test",
                "email": "user@test.com",
                "password_hash": hash_password("user123"),
                "telefono": "555-0001",
                "direccion": "Test Address",
                "estado": "aprobado",
                "rol": "vecino",
                "activo": True
            }
            
            insert_result = table("usuarios").insert(user_data).execute()
            if insert_result.data:
                print(f"✅ Created test user: {insert_result.data[0].get('email')}")
            else:
                print("❌ Failed to create test user")
        
        # List all users
        print("\n📋 All users in database:")
        all_users = table("usuarios").select("id, nombre, email, rol, estado").execute()
        if all_users.data:
            for u in all_users.data:
                print(f"  - {u.get('email')} ({u.get('rol')}) - {u.get('estado')}")
        else:
            print("  No users found")
        
        print("\n✅ Test complete!")
        print("\nYou can now test login with:")
        print("  Email: admin@test.com")
        print("  Password: admin123")
        print("or")
        print("  Email: user@test.com")
        print("  Password: user123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_database())
