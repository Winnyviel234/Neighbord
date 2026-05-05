from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Neighbord Community System"
    environment: str = "development"
    frontend_url: str = "http://localhost:5173"

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    database_url: str = ""

    jwt_secret_key: str = "cambia-esta-clave"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    admin_name: str = "Administrador Neighbord"
    admin_email: str = "admin@gmail.com"
    admin_password: str = "CambiaEstaClave123"

    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_from_name: str = "Neighbord"
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"

    # WhatsApp / Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""
    whatsapp_enabled: bool = False

    # Optional caching and search
    redis_url: str = ""
    elasticsearch_url: str = ""

    # Rate limiting
    rate_limit_requests_per_minute: int = 60

    # Strike API Configuration
    strike_api_key: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
