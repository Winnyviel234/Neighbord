from pathlib import Path
import os
import sys
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

# Asegurar que el directorio backend esté en sys.path para poder importar app.core
sys.path.insert(0, str(BASE_DIR))

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("ERROR: Falta SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY en backend/.env")
    sys.exit(1)

from app.core.supabase import table

try:
    print("Verificando conexión a Supabase...")
    result = table("usuarios").select("id").limit(1).execute()
    if result.data is None:
        print("ERROR: No se pudo leer datos de Supabase. Revisa tus credenciales y la URL.")
        sys.exit(1)
    print("Conexión a Supabase exitosa.")
    print(f"Registros consultados: {len(result.data)}")
    sys.exit(0)
except Exception as exc:
    print(f"ERROR: No se pudo conectar a Supabase: {exc}")
    sys.exit(1)
