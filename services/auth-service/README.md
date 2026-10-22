# Microservice Auth Service (Supervision SOC & RBAC)
**PROJECT RESILIENCE-ALPHA — Workshop M2 EPSI 2026**

Microservice d'authentification et de contrôle d'accès basé sur les rôles (RBAC) pour la console de supervision SOC, garantissant la conformité avec les réglementations **DORA** et **NIS2**.

---

## 🔐 Périmètre d'Authentification

Conformément à la matrice d'architecture cyber-résiliente :
- 💳 **Terminal de Paiement (`/`) :** Reste **ouvert et sans authentification** pour simuler un service public de paiement par carte.
- 🔴 **Console Attaquant (`Attaquant/`) :** Reste **totalement découplée** pour simuler un attaquant externe hostile.
- 🛡️ **Console de Supervision SOC (`/supervision`) :** Strictement verrouillée par authentification cryptographique **JWT Bearer**.

---

## 👥 Comptes Opérateurs SOC Pré-configurés

| Utilisateur | Mot de passe | Rôle | Permissions |
| :--- | :--- | :--- | :--- |
| **`admin`** | `socadmin2026!` | **SOC Administrator** | `READ_METRICS`, `TRIGGER_REMEDIATION`, `CLEAR_LOGS`, `MANAGE_CHAOS` |
| **`operator`** | `operator2026!` | **SOC Analyst** | `READ_METRICS`, `TRIGGER_REMEDIATION` |
| **`auditor`** | `auditor2026!` | **Compliance Auditor** | `READ_METRICS`, `READ_AUDIT_LOGS` |

---

## 🛠️ Spécification des Endpoints

| Méthode | Route | Description | Code Succès |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/login` | Authentifier un opérateur SOC et émettre un jeton JWT Bearer | `200 OK` |
| `GET` | `/api/v1/auth/verify` | Valider la signature et l'expiration d'un jeton (Header `Authorization: Bearer <token>`) | `200 OK` |
| `GET` | `/api/v1/auth/roles` | Lister les rôles et identités disponibles pour la démonstration | `200 OK` |
| `GET` | `/health` | Sonde de santé opérationnelle du service | `200 OK` |

---

## ⚙️ Variables d'Environnement

| Variable | Défaut | Description |
| :--- | :--- | :--- |
| `SERVICE_NAME` | `auth-service` | Identifiant du microservice |
| `PORT` | `8002` | Port d'écoute Uvicorn interne |
| `JWT_SECRET` | `soc-resilience-secret-key-2026` | Clé secrète de signature HMAC-SHA256 |
| `JWT_ALGORITHM` | `HS256` | Algorithme de signature cryptographique |
| `JWT_EXPIRATION_HOURS` | `8` | Durée de validité de la session opérateur |

---

## 💻 Exécution Locale & Tests

```powershell
# Exécution locale
$env:PYTHONPATH="services/auth-service"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# Tests unitaires
$env:PYTHONPATH="services/auth-service"
python -m pytest services/auth-service/tests -v
```
