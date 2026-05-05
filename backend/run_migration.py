#!/usr/bin/env python3
"""
Migration script for Neighbord v2.0
Run this script to apply database migrations for the new modular architecture.
"""

import httpx
from app.core.config import settings

def execute_sql(sql: str):
    """Execute SQL using Supabase REST API"""
    url = f"{settings.supabase_url}/rest/v1/rpc/exec_sql"
    headers = {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json"
    }
    
    # Note: This is a simplified approach. In production, use proper migration tools
    # For now, we'll execute statements one by one
    try:
        response = httpx.post(url, json={"sql": sql}, headers=headers)
        if response.status_code == 200:
            return True
        else:
            print(f"SQL Error: {response.text}")
            return False
    except Exception as e:
        print(f"Request Error: {e}")
        return False

def run_migration():
    """Execute database migration"""
    try:
        print("Starting migration...")
        print("Note: This script uses simplified SQL execution.")
        print("For production, use proper database migration tools.\n")

        # Read migration SQL
        with open('migration_v2.sql', 'r', encoding='utf-8') as f:
            sql = f.read()

        # Split by semicolon and execute each statement
        statements = [s.strip() for s in sql.split(';') if s.strip() and not s.startswith('--')]

        success_count = 0
        for i, stmt in enumerate(statements, 1):
            if stmt:
                print(f"Executing statement {i}...")
                if execute_sql(stmt):
                    success_count += 1
                    print(f"✓ Statement {i} executed successfully")
                else:
                    print(f"✗ Statement {i} failed")

        print(f"\nMigration completed! {success_count}/{len(statements)} statements executed.")
        print("\nNext steps:")
        print("1. Verify tables were created in Supabase dashboard")
        print("2. Test the new API endpoints")
        print("3. Update frontend to use new endpoints")

    except Exception as e:
        print(f"Migration failed: {e}")
        print("Make sure your .env file has correct Supabase credentials")

if __name__ == "__main__":
    run_migration()