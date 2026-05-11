import os
from app.core.supabase import table
from dotenv import load_dotenv

load_dotenv()

try:
    print("Populating roles table...")
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
            if "duplicate key" in str(e).lower() or "already exists" in str(e).lower():
                print(f"  Role {role['name']} already exists")
            else:
                print(f"  Error creating role {role['name']}: {e}")

    print("\nPopulating sectors table...")
    sectors_data = [
        {"name": "Comunidad Principal", "description": "Sector principal de la comunidad"}
    ]

    for sector in sectors_data:
        try:
            result = table("sectors").insert(sector).execute()
            print(f"  Created sector: {sector['name']}")
        except Exception as e:
            if "duplicate key" in str(e).lower() or "already exists" in str(e).lower():
                print(f"  Sector {sector['name']} already exists")
            else:
                print(f"  Error creating sector {sector['name']}: {e}")

    print("\nDone!")

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()