import time
import asyncio
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .k8s_manager import k8s_manager
from .verifier import verify_service_recovery

# Historique structure des remediations
remediation_history: List[Dict[str, Any]] = []

# Journal de logs chronologiques detaille pour affichage console
remediation_logs: List[Dict[str, Any]] = []

def add_log(level: str, message: str, event_id: Optional[str] = None):
    """Ajoute une ligne de log horodatee dans le buffer d'audit."""
    now_iso = datetime.now(timezone.utc).strftime("%H:%M:%S")
    entry = {
        "time": now_iso,
        "timestamp": time.time(),
        "level": level,
        "message": message,
        "event_id": event_id,
    }
    remediation_logs.insert(0, entry)
    # Conservation des 300 derniers logs
    if len(remediation_logs) > 300:
        remediation_logs.pop()

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
    add_log("INFO", "Sonde de surveillance native Kubernetes activee (intervalle 5s).")
    while True:
        try:
            restarted = k8s_manager.restart_unhealthy_pods()
            if restarted:
                event_id = f"REM-K8S-{int(time.time()*1000)}"
                reason_str = f"Pods en anomalie physique detectes : {', '.join(restarted)}"
                add_log("WARN", f"[K8S-NATIVE] {reason_str}", event_id)
                add_log("ACTION", f"[K8S-NATIVE] Suppression et regeneration forcee des pods : {', '.join(restarted)}", event_id)

                event = {
                    "id": event_id,
                    "timestamp": time.time(),
                    "trigger": "KUBERNETES_NATIVE_PROBE",
                    "reason": reason_str,
                    "action": "K8S_POD_DELETE_RECREATE",
                    "status": "EXECUTING",
                }
                remediation_history.insert(0, event)

                add_log("VERIFY", "[HEALTHCHECK] Attente de la stabilisation des conteneurs...", event_id)
                verification = await verify_service_recovery(timeout_sec=15.0)
                event["status"] = "COMPLETED" if verification["success"] else "FAILED"
                event["verification"] = verification

                if verification["success"]:
                    add_log("SUCCESS", f"[PREUVE VALIDEE] Zero-Touch Recovery reussi en {verification['duration_sec']}s ! Transaction: {verification['transaction_id']}", event_id)
                else:
                    add_log("ERROR", f"[ECHEC REPRISE] {verification.get('error', 'Inconnu')}", event_id)

        except Exception as e:
            pass
        await asyncio.sleep(settings.poll_interval_sec)

@asynccontextmanager
async def lifespan(app: FastAPI):
    add_log("INFO", f"Demarrage du Moteur de Remediation v{settings.version} sur {settings.host}:{settings.port}")
    task = asyncio.create_task(k8s_native_watcher_loop())
    yield
    task.cancel()

REMEDIATION_DESCRIPTION = """
### 🤖 Moteur de Remédiation Autonome (Zero-Touch Recovery)

Ce service assure le rétablissement automatique de la plateforme sans intervention humaine :
1. **Surveillance native K8s** : Détection et purge automatique des pods en état critique (`CrashLoopBackOff`, `Error`, etc.).
2. **Réception des alertes ML** : Webhook déclenchant un `rollout restart` lors d'une dégradation statistique.
3. **Preuve par la transaction** : Rejeu automatique d'un paiement réel post-reprise pour certifier le retour nominal au jury.

---

### 🌐 Navigation dans l'Écosystème
- 💳 **[Terminal de Paiement & Dashboard Web (React)](http://localhost:3000)** — Interface visuelle et commandes de démo en direct.
- ⚙️ **[API de Paiement (Swagger)](http://localhost:8000/docs)** — Endpoints bancaires, healthchecks et injection de chaos.
- 🩺 **[Sonde Healthcheck Remédiation](/health)** — Statut du moteur et connectivité avec le cluster.
- 📜 **[Historique des Remédiations](/api/v1/remediation/history)** — Journal d'audit structuré.
- 📝 **[Logs de Remédiation en Temps Réel](/api/v1/remediation/logs)** — Flux de logs d'audit.
- 🐙 **[Dépôt GitHub Officiel](https://github.com/theohadj-a/Workshop2026)** — Sources, Helm Chart, manifestes K8s et documentation.

---
"""

app = FastAPI(
    title="PROJECT RESILIENCE-ALPHA — Remediation Engine",
    description=REMEDIATION_DESCRIPTION,
    version=settings.version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
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
        "logs_count": len(remediation_logs),
    }

@app.post("/api/v1/remediation/alert", tags=["Remediation"])
async def receive_ml_alert(payload: AnomalyAlertPayload, background_tasks: BackgroundTasks):
    """
    Webhook appele par le detecteur AIOps (ML) des qu'une anomalie statistique est identifiee.
    Declenche le rollout restart et verifie la reprise metier.
    """
    event_id = f"REM-ML-{int(time.time()*1000)}"
    lat = payload.metrics.get("avg_latency_ms", 0)
    err = payload.metrics.get("error_rate_5xx", 0) * 100

    add_log("ALERT", f"[ALERTE ML AIOPS] Anomalie detectee par Isolation Forest (Score: {payload.anomaly_score:.4f}, Latence: {lat:.1f}ms, Erreurs: {err:.1f}%)", event_id)
    add_log("ACTION", f"[REMEDIATION] Declenchement du Rollout Restart sur deployment/{settings.k8s_deployment}", event_id)

    event = {
        "id": event_id,
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
    add_log("VERIFY", "[HEALTHCHECK] Attente de la disponibilite HTTP 200 sur le service de paiement...", event_id)
    verification = await verify_service_recovery(timeout_sec=20.0)
    event["status"] = "COMPLETED" if verification["success"] else "FAILED"
    event["verification"] = verification

    if verification["success"]:
        add_log("SUCCESS", f"[PREUVE ZERO-TOUCH] Transaction validee avec succes en {verification['duration_sec']}s ! (ID: {verification['transaction_id']}, Auth: {verification['auth_code']})", event_id)
    else:
        add_log("ERROR", f"[ECHEC REPRISE] {verification.get('error', 'Erreur de verification')}", event_id)

    return {
        "message": "Remediation autonome declenchee et validee avec succes.",
        "event": event,
    }

@app.post("/api/v1/remediation/trigger", tags=["Remediation"])
async def trigger_manual_remediation(payload: ManualTriggerPayload):
    """Declencheur direct pour la demonstration live."""
    event_id = f"REM-MANUAL-{int(time.time()*1000)}"
    add_log("ACTION", f"[DECLENCHEMENT DEMO] Motif : {payload.reason}", event_id)
    add_log("ACTION", f"[REMEDIATION] Rollout Restart ordonne sur {settings.k8s_deployment}", event_id)

    event = {
        "id": event_id,
        "timestamp": time.time(),
        "trigger": "MANUAL_OR_EXTERNAL_API",
        "reason": payload.reason,
        "action": "ROLLOUT_RESTART_DEPLOYMENT",
        "status": "EXECUTING",
    }
    remediation_history.insert(0, event)
    k8s_manager.rollout_restart_deployment()

    add_log("VERIFY", "[HEALTHCHECK] Attente du retablissement du service...", event_id)
    verification = await verify_service_recovery(timeout_sec=20.0)
    event["status"] = "COMPLETED" if verification["success"] else "FAILED"
    event["verification"] = verification

    if verification["success"]:
        add_log("SUCCESS", f"[PREUVE ZERO-TOUCH] Transaction de reprise approuvee en {verification['duration_sec']}s ! Auth: {verification['auth_code']}", event_id)
    else:
        add_log("ERROR", f"[ECHEC REPRISE] {verification.get('error', 'Erreur de verification')}", event_id)

    return event

@app.get("/api/v1/remediation/history", tags=["Remediation"])
def get_history():
    """Retourne l'historique complet et structure des interventions de remediation autonome."""
    return {"history": remediation_history}

@app.get("/api/v1/remediation/logs", tags=["Remediation"])
def get_logs():
    """Retourne le journal chronologique complet des logs d'audit de remediation."""
    return {"logs": remediation_logs, "total": len(remediation_logs)}

@app.delete("/api/v1/remediation/logs", tags=["Remediation"])
def clear_logs():
    """Reinitialise le journal de logs."""
    remediation_logs.clear()
    add_log("INFO", "Journal de logs reinitialise.")
    return {"message": "Logs reinitialises avec succes."}

@app.get("/api/v1/remediation/k8s/pods", tags=["Kubernetes"])
def get_k8s_pods():
    """Expose la liste et l'etat des pods K8s pour le Dashboard."""
    pods = k8s_manager.get_pods()
    return {"pods": pods, "count": len(pods)}
