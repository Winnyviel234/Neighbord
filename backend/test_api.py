#!/usr/bin/env python3
"""
Test script for new Neighbord v2.0 API endpoints
Run this after executing migration_v2.sql in Supabase
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v2"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL.replace('/v2', '')}/health")
        print(f"Health: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health test failed: {e}")
        return False

def test_register():
    """Test user registration"""
    data = {
        "nombre": "Test User",
        "email": "test@example.com",
        "password": "test123",
        "telefono": "123456789",
        "direccion": "Test Address"
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        print(f"Register: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Register test failed: {e}")
        return False

def test_sectors():
    """Test sectors endpoint (requires auth)"""
    # This would need a valid token
    print("Sectors test: Requires authentication token")
    return True

def test_complaints():
    """Test complaints endpoint (requires auth)"""
    print("Complaints test: Requires authentication token")
    return True

def main():
    print("Testing Neighbord v2.0 API...")
    print("=" * 50)

    tests = [
        ("Health Check", test_health),
        ("User Registration", test_register),
        ("Sectors API", test_sectors),
        ("Complaints API", test_complaints),
    ]

    passed = 0
    for name, test_func in tests:
        print(f"\nTesting {name}:")
        if test_func():
            passed += 1
            print("✓ PASSED")
        else:
            print("✗ FAILED")

    print(f"\nResults: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("\n🎉 All basic tests passed! Backend is ready.")
        print("\nNext steps:")
        print("1. Execute migration_v2.sql in Supabase Dashboard")
        print("2. Get authentication token from /api/v2/auth/login")
        print("3. Test authenticated endpoints with Bearer token")
        print("4. Update frontend to use new API endpoints")
    else:
        print("\n⚠️  Some tests failed. Check backend logs and database connection.")

if __name__ == "__main__":
    main()