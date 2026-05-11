import os
from app.core.supabase import table
from dotenv import load_dotenv

load_dotenv()

try:
    users = table('usuarios').select('*').limit(5).execute()
    print('Users in database:')
    if users.data:
        for user in users.data:
            print(f'  ID: {user.get("id")}, Email: {user.get("email")}, Estado: {user.get("estado")}, Rol: {user.get("role_name")}')
    else:
        print('  No users found')
except Exception as e:
    print(f'Error: {e}')