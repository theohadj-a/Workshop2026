import time
import httpx
import logging
from typing import Dict, Any
from .config import settings

logger = logging.getLogger("RemediationVerifier")

def verify_service_recovery(timeout_sec: float = 20.0) -> Dict[str, Any]:
    """
    Attend que le service de paiement soit operationnel et execute une transaction
    bancaire fictive reelle pour prouver le retablissement sans intervention humaine.
    """
    client = httpx.Client(timeout=4.0)
    start_time = time.time()
    health_url = f"{settings.payment_api_url}/health"
    payment_url = f"{settings.payment_api_url}/api/v1/payments"

    logger.info("Attente du retablissement du service (Healthcheck)...")
    is_up = False
    while time.time() - start_time < timeout_sec:
        try:
            res = client.get(health_url)
            if res.status_code == 200:
                is_up = True
                break
        except Exception:
            pass
        time.sleep(1.0)

    if not is_up:
        logger.error("Le service de paiement ne repond pas apres le delai de remédiation.")
        return {
            "success": False,
            "stage": "HEALTHCHECK_FAILED",
            "error": "Le service n'a pas valide le healthcheck a temps.",
            "duration_sec": round(time.time() - start_time, 2),
        }

    # Rejeu d'une transaction bancaire fictive pour la PREUVE DE REPRISE
    logger.info("Service UP ! Execution de la transaction fictive de validation post-reprise...")
    payload = {
        "amount": 10.00,
        "currency": "EUR",
        "customer_name": "Zero-Touch Recovery Agent",
        "customer_email": "recovery.agent@resilience.local",
        "card_number": "4532999988887777",
        "card_expiry": "12/29",
        "card_cvv": "999",
        "merchant_id": "REMEDIATION-CHECKER",
        "reference": f"RECOVERY-PROVED-{int(time.time())}"
    }

    try:
        tx_res = client.post(payment_url, json=payload)
        if tx_res.status_code == 201:
            data = tx_res.json()
            total_duration = round(time.time() - start_time, 2)
            logger.info(f"Transaction de preuve REUSSIE ! ID: {data['transaction_id']} (Temps total de reprise: {total_duration}s)")
            return {
                "success": True,
                "stage": "TRANSACTION_VERIFIED",
                "transaction_id": data["transaction_id"],
                "auth_code": data["auth_code"],
                "duration_sec": total_duration,
                "message": "Zero-Touch Recovery complete : nouvelle transaction traitee avec succes.",
            }
        else:
            return {
                "success": False,
                "stage": "TRANSACTION_REJECTED",
                "error": f"L'API a repondu avec le statut {tx_res.status_code}",
                "duration_sec": round(time.time() - start_time, 2),
            }
    except Exception as e:
        return {
            "success": False,
            "stage": "TRANSACTION_EXCEPTION",
            "error": str(e),
            "duration_sec": round(time.time() - start_time, 2),
        }
