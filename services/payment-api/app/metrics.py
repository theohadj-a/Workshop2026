from prometheus_client import Counter, Histogram, Gauge

# Compteurs HTTP pour l'observabilité globale
REQUEST_COUNT = Counter(
    "payment_http_requests_total",
    "Nombre total de requêtes HTTP reçues",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "payment_http_request_duration_seconds",
    "Durée d'exécution des requêtes HTTP en secondes",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# Métriques métier liées aux transactions de paiement
TRANSACTION_COUNT = Counter(
    "payment_transactions_total",
    "Nombre total de transactions de paiement traitées",
    ["status", "currency"],
)

TRANSACTION_VOLUME = Counter(
    "payment_volume_total",
    "Volume financier cumulé des transactions traitées",
    ["currency"],
)

ACTIVE_REQUESTS = Gauge(
    "payment_active_requests",
    "Nombre de requêtes HTTP en cours de traitement",
)

SERVICE_HEALTH = Gauge(
    "payment_service_health",
    "Indicateur de santé du service de paiement (1 = sain, 0 = en panne)",
)
# Par défaut, le service démarre sain
SERVICE_HEALTH.set(1)
