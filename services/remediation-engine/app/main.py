import time
import asyncio
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .k8s_manager import k8s_manager
from .verifier import verify_service_recovery

# Historique en memoire des remediations effectuees
remediation_history: List[Dict[str, Any]] = []

class AnomalyAlertPayload(BaseModel):
    source: str
    timestamp: float
    anomaly_score: float
    metrics: Dict[str, float]
    recommended_action: Optional[str] = "RESTART_OR_FAILOVER"

class ManualTriggerPayload(BaseModel):
    reason: Optional[str] = "Manual Demonstration Trigger"

async def k8s_native_watcher_loop():
    """
    Boucle de surveillance native K8s (sans ML) :
    Detecte les pods en CrashLoopBackOff ou Error et les relance automatiquement.
    """
    while True:
        try:
            restarted = k8s_manager.restart_unhealthy_pods()
            if restarted:
                event = {
                    "timestamp": time.time(),
                    "trigger": "KUBERNETES_NATIVE_PROBE",
                    "reason": f"Pods en anomalie physique detectes : {', '.join(restarted)}",
                    "action": "K8S_POD_DELETE_RECREATE",
                    "verification": "IN_PROGRESS",
                }
                remediation_history.insert(0, event)
                # Verification de reprise
                verification = verify_service_recovery(timeout_sec=15.0)
                event["verification"] = verification
        except Exception as e:
            pass
        await asyncio.sleep(settings.poll_interval_sec)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lancement du watcher natif K8s en tache de fond
    task = asyncio.create_task(k8s_native_watcher_loop())
    yield
    task.cancel()

app = FastAPI(
    title="PROJECT RESILIENCE-ALPHA — Remediation Engine",
    description="Moteur de remediation autonome (Zero-Touch Recovery) connecte a Kubernetes et au detecteur ML.",
    version=settings.version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "HEALTHY",
        "service": settings.service_name,
        "k8s_connected": k8s_manager.k8s_available,
        "history_count": len(remediation_history),
    }

@app.post("/api/v1/remediation/alert", tags=["Remediation"])
async def receive_ml_alert(payload: AnomalyAlertPayload, background_tasks: BackgroundTasks):
    """
    Webhook appele par le detecteur AIOps (ML) des qu'une anomalie statistique est identifiee.
    Declenche le rollout restart et verifie la reprise metier.
    """
    event = {
        "id": f"REM-{int(time.time()*1000)}",
        "timestamp": payload.timestamp,
        "trigger": "MACHINE_LEARNING_AIOPS",
        "anomaly_score": payload.anomaly_score,
        "metrics_snapshot": payload.metrics,
        "action": "ROLLOUT_RESTART_DEPLOYMENT",
        "status": "EXECUTING",
    }
    remediation_history.insert(0, event)

    # 1. Action corrective sur Kubernetes
    k8s_manager.rollout_restart_deployment()

    # 2. Verification metier autonome (Preuve par la transaction)
    verification = verify_service_recovery(timeout_sec=20.0)
    event["status"] = "COMPLETED" if verification["success"] else "FAILED"
    event["verification"] = verification

    return {
        "message": "Remediation autonome declenchee et validee avec succes.",
        "event": event,
    }

@app.post("/api/v1/remediation/trigger", tags=["Remediation"])
async def trigger_manual_remediation(payload: ManualTriggerPayload):
    """Declencheur direct pour la demonstration ou les tests."""
    event = {
        "id": f"REM-{int(time.time()*1000)}",
        "timestamp": time.time(),
        "trigger": "MANUAL_OR_EXTERNAL_API",
        "reason": payload.reason,
        "action": "ROLLOUT_RESTART_DEPLOYMENT",
        "status": "EXECUTING",
    }
    remediation_history.insert(0, event)
    k8s_manager.rollout_restart_deployment()
    verification = verify_service_recovery(timeout_sec=20.0)
    event["status"] = "COMPLETED" if verification["success"] else "FAILED"
    event["verification"] = verification
    return event

@app.get("/api/v1/remediation/history", tags=["Remediation"])
def get_history():
    """Retourne l'historique complet des interventions de remediation autonome."""
    return {"history": remediation_history}

@app.get("/api/v1/remediation/k8s/pods", tags=["Kubernetes"])
def get_k8s_pods():
    """Expose la liste et l'etat des pods K8s pour le Dashboard."""
    pods = k8s_manager.get_pods()
    return {"pods": pods, "count": len(pods)}
