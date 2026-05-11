import os
from app.core.supabase import table
from app.core.security import hash_password
from dotenv import load_dotenv

load_dotenv()

try:
    # Check if roles and sectors exist
    print("Checking roles table...")
    roles = table("roles").select("*").execute()
    print(f"Roles: {len(roles.data) if roles.data else 0}")
    if roles.data:
        for role in roles.data:
            print(f"  {role.get('name')}")

    print("\nChecking sectors table...")
    sectors = table("sectors").select("*").execute()
    print(f"Sectors: {len(sectors.data) if sectors.data else 0}")
    if sectors.data:
        for sector in sectors.data:
            print(f"  {sector.get('name')}")

    # Create a test user
    test_email = "test@example.com"
    test_password = "test123"

    # Check if user already exists
    existing = table('usuarios').select('*').eq('email', test_email).execute()
    if existing.data:
        print(f'\nUser {test_email} already exists')
        user = existing.data[0]
    else:
        # Get the vecino role ID
        role_result = table("roles").select("id").eq("name", "vecino").single().execute()
        role_id = role_result.data["id"]

        # Create new user (without sector_id for now)
        user_data = {
            "nombre": "Test User",
            "email": test_email,
            "password_hash": hash_password(test_password),
            "telefono": "123456789",
            "direccion": "Test Address",
            "estado": "aprobado",
            "activo": True,
            "role_id": role_id
        }
        result = table('usuarios').insert(user_data).execute()
        user = result.data[0]
        print(f'\nCreated test user: {test_email}')

    print(f'\nUser details:')
    print(f'  ID: {user.get("id")}')
    print(f'  Email: {user.get("email")}')
    print(f'  Estado: {user.get("estado")}')
    print(f'  Role ID: {user.get("role_id")}')
    print(f'  Password hash exists: {bool(user.get("password_hash"))}')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()