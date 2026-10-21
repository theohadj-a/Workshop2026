import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    service_name: str = "auth-service"
    version: str = "1.0.0"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8002"))
    jwt_secret: str = os.getenv("JWT_SECRET", "soc-resilience-secret-key-2026")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 8

    class Config:
        env_file = ".env"

settings = Settings()
