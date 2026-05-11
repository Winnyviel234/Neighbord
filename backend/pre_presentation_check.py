#!/usr/bin/env python3
"""
Script de Verificación Pre-Presentación
Ejecuta esto antes de cualquier demo o presentación para asegurar que todo funcione
"""

import os
import sys
import requests
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def check_backend_running():
    """Verifica que el backend esté ejecutándose"""
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Backend: Ejecutándose en puerto 8000")
            return True
        else:
            print(f"⚠️  Backend responde con código {response.status_code}")
            return False
    except:
        print("❌ Backend: No está ejecutándose en puerto 8000")
        print("   Ejecuta: cd backend && python -m uvicorn app.main:app --reload --port 8000")
        return False

def check_frontend_running():
    """Verifica que el frontend esté ejecutándose"""
    ports_to_check = [5173, 5174, 5175, 5176, 5177]
    for port in ports_to_check:
        try:
            response = requests.get(f"http://localhost:{port}", timeout=3)
            if response.status_code == 200:
                print(f"✅ Frontend: Ejecutándose en puerto {port}")
                return True
        except:
            continue

    print("❌ Frontend: No está ejecutándose")
    print("   Ejecuta: cd frontend && npm run dev")
    return False

def check_auth_endpoints():
    """Verifica que los endpoints de autenticación funcionen"""
    base_url = "http://127.0.0.1:8000"

    # Verificar endpoint de registro
    try:
        import time
        test_email = f"test_{int(time.time())}@example.com"  # Email único
        
        response = requests.post(
            f"{base_url}/api/v2/auth/register",
            json={
                "nombre": "Test User",
                "email": test_email,
                "password": "test123",
                "telefono": "123456789",
                "direccion": "Test Address"
            },
            timeout=10
        )

        if response.status_code in [200, 201]:
            print("✅ Auth Register: Funcionando")
        elif response.status_code == 409:
            print("✅ Auth Register: Funcionando (usuario ya existe)")
        else:
            print(f"⚠️  Auth Register: Código {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Auth Register: Error - {e}")

    # Verificar endpoint de login con usuario de prueba
    try:
        response = requests.post(
            f"{base_url}/api/v2/auth/login",
            json={
                "email": "test@neighbord.com",
                "password": "test123"
            },
            timeout=10
        )

        if response.status_code == 200:
            print("✅ Auth Login: Funcionando")
            return True
        else:
            print(f"⚠️  Auth Login: Código {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Auth Login: Error - {e}")
        return False

def check_cors():
    """Verifica configuración CORS"""
    try:
        headers = {
            "Origin": "http://localhost:5177",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization"
        }
        response = requests.options(
            "http://127.0.0.1:8000/api/v2/auth/me",
            headers=headers,
            timeout=5
        )

        if "access-control-allow-origin" in response.headers:
            print("✅ CORS: Configurado correctamente")
            return True
        else:
            print("⚠️  CORS: Headers no encontrados")
            return False
    except Exception as e:
        print(f"❌ CORS: Error - {e}")
        return False

def check_database():
    """Verifica conexión a base de datos"""
    try:
        from app.core.supabase import table
        result = table("usuarios").select("count").limit(1).execute()
        print("✅ Base de datos: Conectada")
        return True
    except Exception as e:
        print(f"❌ Base de datos: Error - {e}")
        return False

def main():
    """Función principal de verificación"""
    print("🔍 Verificación Pre-Presentación Neighbord")
    print("=" * 50)

    checks = [
        ("Base de datos", check_database),
        ("Backend", check_backend_running),
        ("Frontend", check_frontend_running),
        ("CORS", check_cors),
        ("Auth Endpoints", check_auth_endpoints),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n🔍 Verificando {name}...")
        result = check_func()
        results.append(result)

    print("\n" + "=" * 50)
    print("📊 Resultados:")

    all_passed = all(results)
    for i, (name, _) in enumerate(checks):
        status = "✅" if results[i] else "❌"
        print(f"   {status} {name}")

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ¡Todo listo para la presentación!")
        print("🌐 Frontend: http://localhost:5177")
        print("🔐 Usuario demo: demo@neighbord.com / demo123")
    else:
        print("⚠️  Algunos checks fallaron. Revisa los errores arriba.")
        print("💡 Ejecuta: python initialize_system.py")

    return all_passed

if __name__ == "__main__":
    success = main()
    input("\nPresiona Enter para continuar...")
    sys.exit(0 if success else 1)