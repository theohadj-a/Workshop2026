import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt

from .config import settings

app = FastAPI(
    title="PROJECT RESILIENCE-ALPHA — Authentication Service",
    description="Microservice d'authentification et de contrôle d'accès pour la supervision SOC et la cyber-résilience.",
    version=settings.version,
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

# Base d'utilisateurs opérateurs autorisés pour la supervision SOC
SOC_USERS = {
    "admin": {
        "password": "socadmin2026!",
        "name": "Administrateur SOC",
        "role": "SOC Administrator",
        "permissions": ["READ_METRICS", "TRIGGER_REMEDIATION", "CLEAR_LOGS", "MANAGE_CHAOS"],
    },
    "operator": {
        "password": "operator2026!",
        "name": "Analyste Cyber SOC",
        "role": "SOC Analyst",
        "permissions": ["READ_METRICS", "TRIGGER_REMEDIATION"],
    },
    "auditor": {
        "password": "auditor2026!",
        "name": "Auditeur DORA / NIS2",
        "role": "Compliance Auditor",
        "permissions": ["READ_METRICS", "READ_AUDIT_LOGS"],
    },
}

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

def create_jwt_token(username: str, user_info: Dict[str, Any]) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(hours=settings.jwt_expiration_hours)
    payload = {
        "sub": username,
        "name": user_info["name"],
        "role": user_info["role"],
        "permissions": user_info["permissions"],
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": "resilience-auth-service",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def verify_token(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton d'authentification Bearer manquant ou invalide.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session de supervision expirée. Veuillez vous reconnecter.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signature de jeton cryptographique invalide.",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "HEALTHY",
        "service": settings.service_name,
        "version": settings.version,
    }

@app.post("/api/v1/auth/login", response_model=TokenResponse, tags=["Authentication"])
def login(creds: LoginRequest):
    """Authentifie un opérateur SOC et émet un jeton JWT Bearer."""
    user = SOC_USERS.get(creds.username)
    if not user or user["password"] != creds.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants opérateur incorrects.",
        )

    token = create_jwt_token(creds.username, user)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_expiration_hours * 3600,
        user={
            "username": creds.username,
            "name": user["name"],
            "role": user["role"],
            "permissions": user["permissions"],
        },
    )

@app.get("/api/v1/auth/verify", tags=["Authentication"])
def verify(current_user: Dict[str, Any] = Depends(verify_token)):
    """Valide l'authenticité et la validité temporelle d'un jeton JWT."""
    return {
        "valid": True,
        "user": current_user,
    }

@app.get("/api/v1/auth/roles", tags=["Authentication"])
def get_roles():
    """Liste les profils d'accès SOC pré-configurés pour la démonstration."""
    return {
        "roles": [
            {"username": k, "role": v["role"], "name": v["name"]}
            for k, v in SOC_USERS.items()
        ]
    }
