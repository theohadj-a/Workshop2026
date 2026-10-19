# PROJECT RESILIENCE-ALPHA — Workshop M2 EPSI 2026
> **Équipe :** Théo, Mael, Flora, Fely, Aymeric  
> **Objectif :** Cyber-résilience autonome et reprise sans intervention humaine (*Zero-Touch Recovery*).

---

## 📁 Architecture du Dépôt

```text
Code/
├── docker-compose.yml          # Orchestration des conteneurs
├── .gitignore                  # Fichiers exclus (secrets, venv, db)
├── services/
│   ├── payment-api/            # API FastAPI de paiement fictif (instrumentée Prometheus)
│   ├── auth-service/           # Service d'authentification (JWT)
│   ├── remediation-engine/     # Moteur de reprise autonome (Zero-Touch)
│   └── dashboard-ui/           # Front-end React + Tailwind de supervision
├── ai-ops/
│   └── detector/               # Détection d'anomalies ML AIOps (Isolation Forest Scikit-Learn)
├── security/
│   ├── waf/                    # Reverse Proxy Nginx & filtrage applicatif
│   ├── red-team/               # Scripts d'attaque (exécutés depuis le PC Attaquant)
│   └── secrets/                # Gestion sécurisée des secrets (Vault / SOPS)
├── infra/
│   ├── ansible/                # Playbooks Ansible de déploiement et de reprise
│   └── monitoring/             # Stack d'observabilité (Prometheus, Loki, Grafana)
└── docs/
    ├── ebios-rm/               # Analyse des risques EBIOS Risk Manager
    └── governance/             # PCA/PRA, conformité NIS2 & DORA
```

---

## 🚀 Démarrage Rapide

### 1. Prérequis
- Python 3.13+ (pour exécution locale)
- Docker Desktop & Docker Compose (pour conteneurisation)

### 2. Démarrage de l'API de paiement

#### Option A : En conteneur Docker
```bash
docker compose up --build
```
L'API est exposée sur `http://localhost:8000`.

#### Option B : En local avec l'environnement virtuel Python
```bash
# Activation du venv
.venv\Scripts\activate   # Windows
# ou source .venv/bin/activate # Linux/Mac

# Exécution des tests unitaires
$env:PYTHONPATH="services/payment-api"
python -m pytest services/payment-api/tests -v

# Lancement du serveur
python -m uvicorn app.main:app --app-dir services/payment-api --host 0.0.0.0 --port 8000 --reload
```

---

## 🔍 Points d'accès clés de l'API de paiement
- **Documentation OpenAPI / Swagger** : `http://localhost:8000/docs`
- **Contrôle de santé (Healthcheck)** : `http://localhost:8000/health`
- **Métriques Prometheus** : `http://localhost:8000/metrics`
- **Endpoints de paiement** : `POST /api/v1/payments`, `GET /api/v1/payments`
- **Simulation de trafic** : `POST /api/v1/payments/simulate`
- **Injection de Chaos (Tests)** : `/api/v1/chaos/status`, `/api/v1/chaos/configure`, `/api/v1/chaos/crash`, `/api/v1/chaos/reset`
