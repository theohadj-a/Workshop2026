import os
from pydantic import BaseModel


class Settings(BaseModel):
    service_name: str = os.getenv("SERVICE_NAME", "payment-api")
    version: str = os.getenv("SERVICE_VERSION", "1.0.0")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    db_path: str = os.getenv("DB_PATH", "payments.db")
    database_url: str = os.getenv("DATABASE_URL", "")
    environment: str = os.getenv("ENVIRONMENT", "development")
    cors_origins: list[str] = ["*"]

    # État dynamique du chaos injecté (pour simulation de panne)
    injected_latency_ms: float = float(os.getenv("CHAOS_LATENCY_MS", "0.0"))
    injected_error_rate: float = float(os.getenv("CHAOS_ERROR_RATE", "0.0"))  # Entre 0.0 et 1.0


settings = Settings()
