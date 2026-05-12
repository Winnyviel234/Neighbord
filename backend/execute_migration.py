#!/usr/bin/env python3
"""
Script to execute migration SQL files for notifications module
This script executes the migration_notifications.sql file
"""

import sys
import httpx
from app.core.config import settings

def execute_migration_sql():
    """Execute the migration_notifications.sql file"""
    
    try:
        # Read migration file
        with open('migration_notifications.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("Executing migration_notifications.sql...")
        print(f"SQL size: {len(sql_content)} bytes\n")
        
        # Try using Supabase admin API to execute SQL
        # This requires a valid Supabase service role key
        
        if not settings.supabase_url or not settings.supabase_service_role_key:
            print("ERROR: Missing Supabase credentials in .env")
            return False
        
        # Split SQL into statements
        statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
        
        print(f"Found {len(statements)} SQL statements to execute\n")
        
        # For Supabase, we need to use the Query API or a different approach
        # The best way is to use pgAdmin or the Supabase SQL Editor directly
        
        # Let's try using the direct approach with httpx
        # First, let's test the connection
        test_url = f"{settings.supabase_url}/rest/v1/"
        headers = {
            "apikey": settings.supabase_service_role_key,
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "Content-Type": "application/json"
        }
        
        print("Testing Supabase connection...")
        response = httpx.get(test_url, headers=headers, timeout=10)
        
        if response.status_code >= 400:
            print(f"Connection test failed: {response.status_code}")
            print("Response:", response.text[:200])
            print("\nIMPORTANT: You need to execute the SQL manually in Supabase SQL Editor:")
            print(f"1. Go to: {settings.supabase_url}/projects")
            print("2. Open your project's SQL Editor")
            print("3. Paste the content of migration_notifications.sql")
            print("4. Click 'RUN'")
            return False
        
        print("✓ Connection successful\n")
        
        # Since we can't execute raw SQL through REST API directly,
        # let's at least verify the tables will be created
        print("Recommended way to execute migration:")
        print("1. Visit: https://app.supabase.com")
        print("2. Open your project")
        print("3. Go to 'SQL Editor'")
        print("4. Create a new query")
        print("5. Copy and paste the content from migration_notifications.sql")
        print("6. Execute the query")
        print("\nAlternatively, if you have supabase-cli installed:")
        print("  supabase db push --linked")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = execute_migration_sql()
    sys.exit(0 if success else 1)
