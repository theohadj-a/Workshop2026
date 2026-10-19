# Microservice Payment API (Fictif)
**PROJECT RESILIENCE-ALPHA — Workshop M2 2026**

Microservice de traitement des paiements fictifs, instrumenté pour Prometheus et conçu pour la résilience automatique.

---

## 🚀 Fonctionnalités
- **Traitement de paiements simulés** : validation de schéma (montant, carte, client, marchand), génération d'autorisation bancaire fictive.
- **Stockage persistant SQLite** : transactions enregistrées en local ou dans un volume Docker monté.
- **Observabilité native Prometheus** : exposition des métriques HTTP (latence, taux d'erreurs, requêtes/s) et métier (volume, transactions) sur `/metrics`.
- **Contrôle de santé (Healthcheck)** : endpoint `/health` vérifiant la base de données et l'état opérationnel.
- **Module Chaos Engineering** : endpoints d'injection de pannes (latence, erreurs 500, crash) pour tester la détection ML et le moteur de remédiation autonome.
- **Conteneurisation durcie** : utilisateur non-root `appuser:10001` pour la conformité cybersécurité.

---

## 🛠️ Endpoints de l'API

### Métier
| Méthode | Route | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/payments` | Traiter une transaction fictive |
| `GET` | `/api/v1/payments` | Lister les transactions récentes (paginé) |
| `GET` | `/api/v1/payments/{id}` | Obtenir le détail d'une transaction |
| `POST` | `/api/v1/payments/simulate` | Générer un lot de transactions aléatoires |

### Observabilité & Santé
| Méthode | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Statut de santé pour Docker / Prometheus / Remédiation |
| `GET` | `/metrics` | Métriques au format Prometheus |
| `GET` | `/docs` | Documentation interactive OpenAPI (Swagger UI) |

### Chaos Engineering (Simulation d'incident)
| Méthode | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/chaos/status` | Consulter l'état des pannes injectées |
| `POST` | `/api/v1/chaos/configure` | Injecter de la latence ou un taux d'erreurs 500 |
| `POST` | `/api/v1/chaos/crash` | Simuler un crash brutal du processus |
| `POST` | `/api/v1/chaos/reset` | Réinitialiser à l'état nominal |

---

## 💻 Exécution Locale (Sans Docker)

```bash
# Dans le dossier Code/
# Activer le venv
.venv\Scripts\activate   # Windows
# ou source .venv/bin/activate # Linux/Mac

# Lancer le serveur FastAPI
$env:PYTHONPATH="services/payment-api"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
L'API est alors disponible sur `http://localhost:8000` et la documentation Swagger sur `http://localhost:8000/docs`.

---

## 🐳 Exécution avec Docker

```bash
docker build -t payment-api:latest services/payment-api
docker run -p 8000:8000 payment-api:latest
```
