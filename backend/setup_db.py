import os
from app.core.supabase import table
from dotenv import load_dotenv

load_dotenv()

try:
    # Try to select from roles table
    print("Checking if roles table exists...")
    roles = table("roles").select("*").execute()
    print(f"Roles table exists, found {len(roles.data) if roles.data else 0} roles")

    if not roles.data:
        print("Creating roles...")
        roles_data = [
            {"name": "admin", "permissions": ["all"]},
            {"name": "directiva", "permissions": ["manage_users", "manage_meetings", "manage_voting", "manage_finances", "view_reports"]},
            {"name": "tesorero", "permissions": ["manage_finances", "view_reports"]},
            {"name": "vocero", "permissions": ["manage_meetings", "manage_voting", "view_reports"]},
            {"name": "secretaria", "permissions": ["manage_meetings", "view_reports"]},
            {"name": "vecino", "permissions": ["view_public", "submit_complaints", "vote"]}
        ]

        for role in roles_data:
            try:
                result = table("roles").insert(role).execute()
                print(f"  Created role: {role['name']}")
            except Exception as e:
                print(f"  Error creating role {role['name']}: {e}")

    # Try to select from sectors table
    print("\nChecking if sectors table exists...")
    sectors = table("sectors").select("*").execute()
    print(f"Sectors table exists, found {len(sectors.data) if sectors.data else 0} sectors")

    if not sectors.data:
        print("Creating sectors...")
        sectors_data = [
            {"name": "Comunidad Principal", "description": "Sector principal de la comunidad"}
        ]

        for sector in sectors_data:
            try:
                result = table("sectors").insert(sector).execute()
                print(f"  Created sector: {sector['name']}")
            except Exception as e:
                print(f"  Error creating sector {sector['name']}: {e}")

    print("\nDone!")

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()