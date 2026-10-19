import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from .config import settings
from .database import init_db
from .metrics import REQUEST_COUNT, REQUEST_LATENCY, ACTIVE_REQUESTS
from .routers import payments, health, chaos

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialisation de la base de données au démarrage
    init_db()
    yield

app = FastAPI(
    title="PROJECT RESILIENCE-ALPHA — Payment API",
    description="Microservice de paiement fictif conteneurisé et instrumenté pour l'observabilité et la cyber-résilience.",
    version=settings.version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de collecte des métriques Prometheus
@app.middleware("http")
async def prometheus_metrics_middleware(request: Request, call_next):
    ACTIVE_REQUESTS.inc()
    start_time = time.time()
    endpoint = request.url.path

    try:
        response = await call_next(request)
        status_code = str(response.status_code)
    except Exception:
        status_code = "500"
        raise
    finally:
        duration = time.time() - start_time
        ACTIVE_REQUESTS.dec()

        # On normalise les endpoints pour éviter l'explosion de cardinalité
        normalized_endpoint = endpoint
        if endpoint.startswith("/api/v1/payments/") and len(endpoint.split("/")) > 4:
            normalized_endpoint = "/api/v1/payments/{id}"

        REQUEST_LATENCY.labels(method=request.method, endpoint=normalized_endpoint).observe(duration)
        REQUEST_COUNT.labels(method=request.method, endpoint=normalized_endpoint, status_code=status_code).inc()

    return response

# Exposition des métriques Prometheus
@app.get("/metrics", tags=["Observability"])
def get_metrics():
    """Expose les métriques système et métier au format Prometheus."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Route racine d'accueil
@app.get("/", tags=["General"])
def root():
    return {
        "service": settings.service_name,
        "version": settings.version,
        "status": "ONLINE",
        "documentation": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }

# Inclusion des routeurs
app.include_router(health.router)
app.include_router(payments.router)
app.include_router(chaos.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
