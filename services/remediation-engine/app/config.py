import os
from pydantic import BaseModel

class Settings(BaseModel):
    service_name: str = os.getenv("SERVICE_NAME", "remediation-engine")
    version: str = os.getenv("SERVICE_VERSION", "1.0.0")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8001"))
    k8s_namespace: str = os.getenv("K8S_NAMESPACE", "resilience-alpha")
    k8s_deployment: str = os.getenv("K8S_DEPLOYMENT", "payment-api")
    payment_api_url: str = os.getenv("PAYMENT_API_URL", "http://localhost:8000")
    poll_interval_sec: float = float(os.getenv("POLL_INTERVAL_SEC", "5.0"))
    use_mock_k8s: bool = os.getenv("USE_MOCK_K8S", "false").lower() in ("true", "1")

settings = Settings()
