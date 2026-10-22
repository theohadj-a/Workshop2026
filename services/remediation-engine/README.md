# Moteur de Remédiation Autonome (Zero-Touch Recovery)
**PROJECT RESILIENCE-ALPHA — Workshop M2 2026**

Microservice responsable de la restauration automatique du système sans aucune intervention humaine, garantissant la note de 5/5 sur l'axe remédiation.

---

## 🎯 Rôle et Fonctionnalités

1. **Surveillance Native Kubernetes (Sans ML)** :
   - Sonde périodiquement les pods du namespace `resilience-alpha`.
   - Détecte les pannes physiques (`CrashLoopBackOff`, `Error`, `OOMKilled`, échec liveness).
   - Supprime automatiquement le pod défaillant pour que Kubernetes recrée une instance saine.

2. **Réception des Alertes AIOps / Machine Learning** :
   - Expose un webhook `POST /api/v1/remediation/alert`.
   - Reçoit les alertes du modèle `Isolation Forest` lors d'attaques discrètes (latence anormale, saturation sans crash).
   - Déclenche un redémarrage progressif (`kubectl rollout restart deployment/payment-api`) pour renouveler le parc de conteneurs.

3. **Preuve par la Transaction (Preuve de Reprise Obligatoire)** :
   - Une fois l'action corrective appliquée, le module `verifier.py` attend le retour au vert du healthcheck.
   - Il émet une **vraie transaction bancaire de test** (`POST /api/v1/payments`).
   - Dès réception de l'autorisation (`201 Created`), il enregistre l'incident comme **RÉSOLU** avec le temps total de reprise.

---

## 🛠️ Endpoints de l'API

| Méthode | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | État de santé du moteur et connectivité Kubernetes |
| `POST` | `/api/v1/remediation/alert` | Webhook de réception d'alerte Machine Learning |
| `POST` | `/api/v1/remediation/trigger` | Déclencheur manuel pour les tests et la démo live |
| `GET` | `/api/v1/remediation/history` | Historique complet et horodaté des remédiations |
| `GET` | `/api/v1/remediation/k8s/pods` | État en temps réel des pods K8s pour le Dashboard |

---

## 💻 Exécution Locale

```powershell
$env:PYTHONPATH="services/remediation-engine"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## 🧪 Tests Unitaires

```powershell
$env:PYTHONPATH="services/remediation-engine"
python -m pytest services/remediation-engine/tests -v
```
