from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PaymentCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Montant de la transaction (ex: 49.99)")
    currency: str = Field(default="EUR", description="Devise ISO (ex: EUR, USD)")
    customer_name: str = Field(..., min_length=2, description="Nom complet du client fictif")
    customer_email: str = Field(..., min_length=5, description="Email du client fictif")
    card_number: str = Field(..., min_length=12, description="Numéro de carte simulé (ex: 4532XXXXXXXX1234)")
    card_cvv: Optional[str] = Field(default="123", description="Cryptogramme fictif")
    card_expiry: Optional[str] = Field(default="12/28", description="Date d'expiration (MM/YY)")
    merchant_id: str = Field(default="MERCHANT-EPSI-01", description="Identifiant du commerçant partenaire")
    reference: Optional[str] = Field(default=None, description="Référence externe de commande")

class PaymentResponse(BaseModel):
    transaction_id: str
    reference: str
    amount: float
    currency: str
    customer_name: str
    card_last4: str
    merchant_id: str
    status: str
    auth_code: str
    message: str
    created_at: str

class PaymentListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    transactions: List[PaymentResponse]

class BatchSimulationRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=100, description="Nombre de transactions à simuler")
    currency: str = Field(default="EUR")

class BatchSimulationResponse(BaseModel):
    requested: int
    successful: int
    failed: int
    transactions: List[PaymentResponse]

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    uptime_seconds: float
    database_connected: bool
    total_transactions: int

class ChaosUpdateRequest(BaseModel):
    injected_latency_ms: Optional[float] = Field(None, ge=0.0, le=10000.0)
    injected_error_rate: Optional[float] = Field(None, ge=0.0, le=1.0)

class ChaosStatusResponse(BaseModel):
    injected_latency_ms: float
    injected_error_rate: float
    is_active: bool
