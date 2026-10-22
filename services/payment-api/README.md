# Microservice Payment API (Fictif)
**PROJECT RESILIENCE-ALPHA — Workshop M2 EPSI 2026**

Microservice cœur de métier traitant les transactions bancaires simulées. Il est instrumenté nativement pour Prometheus, conteneurisé selon les normes de sécurité non-root et conçu pour la cyber-résilience autonome.

---

## 🚀 Fonctionnalités Clés
- **Traitement transactionnel bancaire** : validation de schéma Pydantic (montant, carte, client, marchand), génération d'autorisations `AUTH-XXXXXX` et persistance.
- **Double moteur de base de données** : PostgreSQL en environnement de production / Kubernetes (Helm), ou SQLite autonome en développement local.
- **Observabilité native Prometheus** : exposition des compteurs de requêtes, histogrammes de latence et requêtes actives sur `/metrics`.
- **Contrôle de santé (Healthcheck)** : endpoint `/health` vérifiant la connectivité DB, l'état opérationnel et l'uptime.
- **Module Chaos Engineering intégré** : endpoints de simulation de pannes (latence artificielle, injection d'erreurs 500, crash brutal) pour éprouver le modèle ML AIOps et le moteur de remédiation.
- **Durcissement de conteneur** : utilisateur non-root (`appuser:10001`), système de fichiers restreint et exclusion des secrets.

---

## 🛠️ Spécification des Endpoints (OpenAPI / Swagger)

Documentation Swagger interactive disponible sur :
- **Via le WAF Nginx (Recommandé) :** [http://localhost:3000/docs](http://localhost:3000/docs) (ou `/redoc`)
- **En accès direct local :** [http://localhost:8000/docs](http://localhost:8000/docs)

### 1. Transactions Métier
| Méthode | Route | Description | Code Succès |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/payments` | Soumettre une nouvelle transaction bancaire | `201 Created` |
| `GET` | `/api/v1/payments` | Consulter les transactions récentes (pagination `limit`/`offset`) | `200 OK` |
| `GET` | `/api/v1/payments/{payment_id}` | Obtenir le reçu détaillé d'une transaction | `200 OK` |
| `POST` | `/api/v1/payments/simulate` | Générer un lot de transactions synthétiques de test | `200 OK` |

### 2. Observabilité & Santé
| Méthode | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Sonde de disponibilité Liveness/Readiness (DB & statut) |
| `GET` | `/metrics` | Métriques au format OpenMetrics / Prometheus |
| `GET` | `/docs` | Interface graphique Swagger UI |
| `GET` | `/openapi.json` | Schéma JSON OpenAPI v3 |

### 3. Chaos Engineering (Contrôle d'Incident)
| Méthode | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/chaos/status` | Consulter les paramètres d'incident actifs |
| `POST` | `/api/v1/chaos/configure` | Injecter de la latence (`injected_latency_ms`) ou des erreurs 500 (`injected_error_rate`) |
| `POST` | `/api/v1/chaos/reset` | Réinitialiser le service aux conditions nominales |
| `POST` | `/api/v1/chaos/crash` | Provoquer l'extinction forcée du conteneur (`exit 1`) |

---

## ⚙️ Variables d'Environnement

| Variable | Défaut | Description |
| :--- | :--- | :--- |
| `SERVICE_NAME` | `payment-api` | Identifiant du service pour les logs et métriques |
| `PORT` | `8000` | Port d'écoute Uvicorn interne |
| `DATABASE_URL` | *(vide)* | Chaîne de connexion PostgreSQL (`postgresql://user:pass@host:5432/db`). Si absente, bascule sur SQLite. |
| `DB_PATH` | `/app/data/payments.db` | Chemin du fichier SQLite local si `DATABASE_URL` n'est pas configuré |
| `CORS_ORIGINS` | `*` | Origines autorisées pour les requêtes Cross-Origin |

---

## 💻 Exécution Locale (Développement)

```powershell
# Activation de l'environnement virtuel
.venv\Scripts\activate

# Lancement avec Uvicorn
$env:PYTHONPATH="services/payment-api"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🧪 Tests Automatisés

```powershell
$env:PYTHONPATH="services/payment-api"
python -m pytest services/payment-api/tests -v
```
