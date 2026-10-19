import os
import sys
import threading
import time
from fastapi import APIRouter, HTTPException, status
from ..config import settings
from ..schemas import ChaosUpdateRequest, ChaosStatusResponse
from ..metrics import SERVICE_HEALTH

router = APIRouter(prefix="/api/v1/chaos", tags=["Chaos Engineering & Testing"])

@router.get("/status", response_model=ChaosStatusResponse)
async def get_chaos_status():
    """Retourne l'état actuel des perturbations injectées."""
    is_active = (settings.injected_latency_ms > 0) or (settings.injected_error_rate > 0)
    return ChaosStatusResponse(
        injected_latency_ms=settings.injected_latency_ms,
        injected_error_rate=settings.injected_error_rate,
        is_active=is_active,
    )

@router.post("/configure", response_model=ChaosStatusResponse)
async def configure_chaos(params: ChaosUpdateRequest):
    """Permet d'injecter une dégradation applicative contrôlée (latence, taux d'erreurs)."""
    if params.injected_latency_ms is not None:
        settings.injected_latency_ms = params.injected_latency_ms
    if params.injected_error_rate is not None:
        settings.injected_error_rate = params.injected_error_rate

    is_active = (settings.injected_latency_ms > 0) or (settings.injected_error_rate > 0)
    return ChaosStatusResponse(
        injected_latency_ms=settings.injected_latency_ms,
        injected_error_rate=settings.injected_error_rate,
        is_active=is_active,
    )

@router.post("/reset", response_model=ChaosStatusResponse)
async def reset_chaos():
    """Réinitialise tous les paramètres d'injection de panne (retour au fonctionnement nominal)."""
    settings.injected_latency_ms = 0.0
    settings.injected_error_rate = 0.0
    SERVICE_HEALTH.set(1)
    return ChaosStatusResponse(
        injected_latency_ms=0.0,
        injected_error_rate=0.0,
        is_active=False,
    )

@router.post("/crash")
async def trigger_crash():
    """
    Simule un crash critique immédiat du processus (SIGTERM/exit).
    Permet de tester le redémarrage automatique Docker et la résilience infra.
    """
    SERVICE_HEALTH.set(0)

    def delayed_exit():
        time.sleep(0.5)
        # Termine le processus Python pour simuler un crash fatal
        os._exit(1)

    threading.Thread(target=delayed_exit, daemon=True).start()
    return {"message": "Service crash initiated. Process will exit in 500ms."}
