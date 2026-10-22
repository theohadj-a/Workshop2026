import time
from fastapi import APIRouter, HTTPException, status
from ..config import settings
from ..database import check_db_health, count_transactions
from ..schemas import HealthResponse
from ..metrics import SERVICE_HEALTH

router = APIRouter(tags=["Health"])

START_TIME = time.time()

@router.get("/health", response_model=HealthResponse)
@router.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """
    Endpoint de contrôle de santé (Healthcheck).
    Utilisé par Docker, Prometheus et le moteur de remédiation pour vérifier la disponibilité réelle.
    """
    db_ok = check_db_health()
    uptime = round(time.time() - START_TIME, 2)
    tx_count = count_transactions() if db_ok else 0

    if not db_ok:
        SERVICE_HEALTH.set(0)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "UNHEALTHY",
                "service": settings.service_name,
                "version": settings.version,
                "uptime_seconds": uptime,
                "database_connected": False,
                "total_transactions": tx_count,
            },
        )

    SERVICE_HEALTH.set(1)
    return HealthResponse(
        status="HEALTHY",
        service=settings.service_name,
        version=settings.version,
        uptime_seconds=uptime,
        database_connected=True,
        total_transactions=tx_count,
    )
