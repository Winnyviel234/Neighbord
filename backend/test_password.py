#!/usr/bin/env python3
"""Test password verification"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.core.supabase import table

def test_login():
    """Test login with admin credentials"""
    try:
        print("🔑 Testing admin login...")
        print(f"   Email: {settings.admin_email}")
        print(f"   Password: {settings.admin_password}")
        
        # Get user from database
        result = table("usuarios").select("*").eq("email", settings.admin_email).execute()
        
        if not result.data or len(result.data) == 0:
            print(f"❌ User not found in database")
            return
        
        user = result.data[0]
        print(f"\n📊 User found:")
        print(f"   ID: {user.get('id')}")
        print(f"   Email: {user.get('email')}")
        print(f"   Role: {user.get('rol')}")
        print(f"   Status: {user.get('estado')}")
        print(f"   Active: {user.get('activo')}")
        print(f"   Password hash (first 20 chars): {user.get('password_hash', '')[:20]}...")
        
        # Test password verification
        print(f"\n🔐 Testing password verification...")
        password_hash = user.get('password_hash')
        password_to_test = settings.admin_password
        
        is_correct = verify_password(password_to_test, password_hash)
        
        if is_correct:
            print(f"✅ Password is CORRECT!")
        else:
            print(f"❌ Password is INCORRECT!")
            print(f"\n   Testing with different passwords...")
            
            # Try some common variations
            test_passwords = [
                "TuClaveAdmin123",
                "tualaveadmin123",
                "admin123",
                "password",
            ]
            
            for pwd in test_passwords:
                if verify_password(pwd, password_hash):
                    print(f"   ✅ Password matched: {pwd}")
                    break
        
        # Check status constraint
        print(f"\n📋 Checking status...")
        allowed_states = ["aprobado", "activo", "pendiente"]
        if user.get("estado") in allowed_states:
            print(f"✅ Status '{user.get('estado')}' is allowed for login")
        else:
            print(f"❌ Status '{user.get('estado')}' is NOT allowed for login")
            print(f"   Allowed states: {allowed_states}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login()
