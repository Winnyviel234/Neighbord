from pathlib import Path
import os

import psycopg
from dotenv import load_dotenv
from passlib.context import CryptContext

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def read_sql(filename: str) -> str:
    return (BASE_DIR / filename).read_text(encoding="utf-8")


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Falta {name} en backend/.env")
    return value


def main():
    database_url = require_env("DATABASE_URL")
    admin_name = os.getenv("ADMIN_NAME", "Administrador Neighbord")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@gmail.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "CambiaEstaClave123")
    
    # Limitar la contraseña a 72 bytes máximo para bcrypt
    admin_password = admin_password[:72]

    schema_sql = read_sql("supabase_schema.sql")
    noticias_sql = read_sql("supabase_noticias.sql")
    password_hash = pwd_context.hash(admin_password)

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            print("Creando tablas, vistas e indices...")
            cur.execute(schema_sql)
            cur.execute(noticias_sql)

            print("Creando o actualizando usuario administrador...")
            cur.execute(
                """
                insert into usuarios (nombre, email, password_hash, rol, estado, activo)
                values (%s, %s, %s, 'admin', 'aprobado', true)
                on conflict (email) do update set
                  nombre = excluded.nombre,
                  password_hash = excluded.password_hash,
                  rol = 'admin',
                  estado = 'aprobado',
                  activo = true;
                """,
                (admin_name, admin_email, password_hash),
            )
        conn.commit()

    print("Base de datos lista.")
    print(f"Admin: {admin_email}")
    print("Entra con la clave configurada en ADMIN_PASSWORD y cambiala despues.")


if __name__ == "__main__":
    main()
