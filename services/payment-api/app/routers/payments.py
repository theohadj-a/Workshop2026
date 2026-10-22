import uuid
import time
import random
import asyncio
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from ..config import settings
from ..schemas import (
    PaymentCreate,
    PaymentResponse,
    PaymentListResponse,
    BatchSimulationRequest,
    BatchSimulationResponse,
)
from ..database import save_transaction, get_transaction_by_id, list_transactions, count_transactions
from ..metrics import TRANSACTION_COUNT, TRANSACTION_VOLUME

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])

# Noms et emails fictifs pour la génération de trafic simulé
SAMPLE_CUSTOMERS = [
    ("Alice Martin", "alice.martin@example.fr"),
    ("Bob Dupont", "bob.dupont@example.fr"),
    ("Charlie Bernard", "charlie.bernard@example.fr"),
    ("David Moreau", "david.moreau@example.fr"),
    ("Emma Petit", "emma.petit@example.fr"),
    ("François Leroy", "francois.leroy@example.fr"),
    ("Guillaume Roux", "guillaume.roux@example.fr"),
]

def mask_card(card_number: str) -> str:
    cleaned = card_number.replace(" ", "").replace("-", "")
    if len(cleaned) < 4:
        return "****"
    return cleaned[-4:]

@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(payment: PaymentCreate):
    """
    Traite une transaction de paiement fictive.
    Enregistre la transaction en base de données et alimente les métriques Prometheus.
    """
    # 1. Gestion du chaos injecté (latence artificielle)
    if settings.injected_latency_ms > 0:
        await asyncio.sleep(settings.injected_latency_ms / 1000.0)

    # 2. Gestion du chaos injecté (taux d'erreurs 500)
    if settings.injected_error_rate > 0:
        if random.random() < settings.injected_error_rate:
            TRANSACTION_COUNT.labels(status="FAILED", currency=payment.currency).inc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Payment processing gateway failure (injected failure)",
            )

    # 3. Création des métadonnées de transaction fictive
    tx_id = str(uuid.uuid4())
    reference = payment.reference or f"REF-{uuid.uuid4().hex[:8].upper()}"
    auth_code = f"AUTH-{random.randint(100000, 999999)}"
    created_at = datetime.now(timezone.utc).isoformat()
    last4 = mask_card(payment.card_number)

    tx_data = {
        "id": tx_id,
        "reference": reference,
        "amount": round(payment.amount, 2),
        "currency": payment.currency.upper(),
        "customer_name": payment.customer_name,
        "customer_email": payment.customer_email,
        "card_last4": last4,
        "merchant_id": payment.merchant_id,
        "status": "APPROVED",
        "auth_code": auth_code,
        "message": "Payment authorized successfully (simulated)",
        "created_at": created_at,
        "error_message": None,
    }

    # 4. Sauvegarde persistante
    try:
        save_transaction(tx_data)
    except Exception as e:
        TRANSACTION_COUNT.labels(status="ERROR", currency=payment.currency).inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database storage error: {str(e)}",
        )

    # 5. Incrément des métriques Prometheus métier
    TRANSACTION_COUNT.labels(status="APPROVED", currency=payment.currency).inc()
    TRANSACTION_VOLUME.labels(currency=payment.currency).inc(payment.amount)

    return PaymentResponse(
        transaction_id=tx_id,
        reference=reference,
        amount=tx_data["amount"],
        currency=tx_data["currency"],
        customer_name=tx_data["customer_name"],
        card_last4=tx_data["card_last4"],
        merchant_id=tx_data["merchant_id"],
        status=tx_data["status"],
        auth_code=auth_code,
        message=tx_data["message"],
        created_at=created_at,
    )

@router.get("", response_model=PaymentListResponse)
async def get_payments(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Retourne la liste paginée des transactions récentes."""
    total = count_transactions()
    rows = list_transactions(limit=limit, offset=offset)

    transactions = [
        PaymentResponse(
            transaction_id=r["id"],
            reference=r["reference"],
            amount=r["amount"],
            currency=r["currency"],
            customer_name=r["customer_name"],
            card_last4=r["card_last4"],
            merchant_id=r["merchant_id"],
            status=r["status"],
            auth_code=r["auth_code"],
            message=r["message"],
            created_at=r["created_at"],
        )
        for r in rows
    ]

    return PaymentListResponse(
        total=total,
        limit=limit,
        offset=offset,
        transactions=transactions,
    )

@router.get("/{transaction_id}", response_model=PaymentResponse)
async def get_payment(transaction_id: str):
    """Récupère le détail d'une transaction via son identifiant unique."""
    row = get_transaction_by_id(transaction_id)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found",
        )

    return PaymentResponse(
        transaction_id=row["id"],
        reference=row["reference"],
        amount=row["amount"],
        currency=row["currency"],
        customer_name=row["customer_name"],
        card_last4=row["card_last4"],
        merchant_id=row["merchant_id"],
        status=row["status"],
        auth_code=row["auth_code"],
        message=row["message"],
        created_at=row["created_at"],
    )

@router.post("/simulate", response_model=BatchSimulationResponse)
async def simulate_traffic(req: BatchSimulationRequest):
    """
    Génère un lot de transactions fictives aléatoires.
    Très utile pour alimenter les métriques pour le modèle ML ou valider l'activité nominale.
    """
    successful = 0
    failed = 0
    results: list[PaymentResponse] = []

    for _ in range(req.count):
        cust_name, cust_email = random.choice(SAMPLE_CUSTOMERS)
        amount = round(random.uniform(5.0, 500.0), 2)
        fake_card = f"4532{random.randint(1000, 9999)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}"

        payload = PaymentCreate(
            amount=amount,
            currency=req.currency,
            customer_name=cust_name,
            customer_email=cust_email,
            card_number=fake_card,
            merchant_id=f"MERCHANT-{random.randint(1, 5):02d}",
        )

        try:
            res = await create_payment(payload)
            results.append(res)
            successful += 1
        except HTTPException:
            failed += 1

    return BatchSimulationResponse(
        requested=req.count,
        successful=successful,
        failed=failed,
        transactions=results,
    )
