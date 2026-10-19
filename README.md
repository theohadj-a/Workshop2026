# PROJECT RESILIENCE-ALPHA — Workshop M2 EPSI 2026
> **Équipe :** Théo, Mael, Flora, Fely, Aymeric  
> **Objectif :** Cyber-résilience autonome et reprise sans intervention humaine (*Zero-Touch Recovery*).

---

## 📁 Architecture du Dépôt

```text
Code/
├── docker-compose.yml              # Orchestrateur local des conteneurs (Payment, Remediation, Dashboard)
├── .gitignore                      # Exclusions (secrets, venv, bases SQLite, builds)
├── services/
│   ├── payment-api/                # API FastAPI de paiement fictif (instrumentée Prometheus)
│   ├── remediation-engine/         # Moteur de reprise autonome (Zero-Touch) relié à K8s & ML
│   ├── dashboard-ui/               # Front-end React + Tailwind (Terminal bancaire & Supervision)
│   └── auth-service/               # Service d'authentification (JWT)
├── ai-ops/
│   └── detector/                   # Détecteur d'anomalies ML (Isolation Forest pré-entraîné Scikit-Learn)
├── security/
│   ├── waf/                        # Reverse Proxy Nginx & filtrage applicatif
│   ├── red-team/                   # Scripts d'attaque (exécutés depuis le PC Attaquant)
│   └── secrets/                    # Gestion sécurisée des secrets (Vault / SOPS)
├── infra/
│   ├── helm/                       # Helm Chart officiel (resilience-alpha) paramétrable
│   ├── k8s/                        # Manifestes Kubernetes natifs (Deployments, Services, HPA, RBAC)
│   ├── ansible/                    # Playbooks Ansible de déploiement et de reprise
│   └── monitoring/                 # Stack d'observabilité (Prometheus, Loki, Grafana)
└── docs/
    ├── ebios-rm/                   # Analyse des risques EBIOS Risk Manager
    └── governance/                 # PCA/PRA, conformité NIS2 & DORA
```

---

## ⚡ Démarrage Rapide

### Option 1 : Docker Compose (Idéal pour le développement local)
Lance l'ensemble de la stack (API de paiement, moteur de remédiation, front-end) en une seule commande :
```bash
docker compose up -d --build
```
- 💳 **Dashboard & Terminal de Paiement** : [http://localhost:3000](http://localhost:3000)
- ⚙️ **API de Paiement (Swagger)** : [http://localhost:8000/docs](http://localhost:8000/docs)
- 🩺 **API Healthcheck** : [http://localhost:8000/health](http://localhost:8000/health)
- 📊 **Métriques Prometheus** : [http://localhost:8000/metrics](http://localhost:8000/metrics)
- 🤖 **Moteur de Remédiation** : [http://localhost:8001/health](http://localhost:8001/health)

Pour stopper la stack :
```bash
docker compose down
```

---

### Option 2 : Kubernetes avec Helm (Haute Disponibilité & Réplicas)
Déploie l'application sur un cluster Kubernetes avec **3 réplicas** pour l'API, auto-scaling horizontal (HPA), RBAC et NetworkPolicy.

```bash
# Déploiement via Helm
helm install resilience-alpha ./infra/helm/resilience-alpha

# Ou mise à jour dynamique
helm upgrade --install resilience-alpha ./infra/helm/resilience-alpha
```
- Le Dashboard est exposé sur le NodePort : `http://localhost:30080`
- Pour modifier les réplicas à la volée :
  ```bash
  helm upgrade --install resilience-alpha ./infra/helm/resilience-alpha --set paymentApi.replicaCount=5
  ```

---

### Option 3 : Kubernetes Natif (Sans Helm)
```bash
kubectl apply -f infra/k8s/
```
Pour inspecter les pods :
```bash
kubectl get pods -n resilience-alpha -o wide
```

---

## 🧠 Détection d'Anomalies Machine Learning (AIOps)

La détection repose sur un modèle non supervisé **Isolation Forest** (Scikit-Learn) clé en main, sans dépendance GPU.

- **Modèle pré-entraîné** : `ai-ops/detector/model_isolation_forest.joblib`
- **Générer / Ré-entraîner la baseline nominale** :
  ```bash
  python ai-ops/detector/train_baseline.py
  ```
- **Lancer la boucle de surveillance temps réel** :
  ```bash
  python ai-ops/detector/detector.py
  ```
- **Tester une prédiction instantanée (Nominal vs Attaque)** :
  ```bash
  python ai-ops/detector/detector.py --test
  ```

Dès qu'une anomalie statistique est identifiée (latence anormale, pic d'erreurs 5xx, saturation), le détecteur envoie automatiquement un webhook au **Moteur de Remédiation**.

---

## 🛡️ Moteur de Remédiation Autonome (Zero-Touch Recovery)

Le moteur [`services/remediation-engine`](file:///c:/Users/buzz_/Bureau/code/Workshop/Code/services/remediation-engine) opère sur deux niveaux :
1. **Surveillance native K8s (sans ML)** : interroge périodiquement l'état des conteneurs. Si un pod est en panne physique (`CrashLoopBackOff`, `Error`, `OOMKilled`), il force son redémarrage.
2. **Réaction à l'alerte ML** : déclenche un `rollout restart` progressif du déploiement en cas de dégradation statistique subtile (que K8s ne détecte pas comme un crash).
3. **Preuve par la transaction** : dès que le service est restauré, le moteur émet automatiquement un paiement réel de validation (`POST /api/v1/payments`) et certifie le rétablissement au jury.

---

## 🧪 Tests Automatisés

```powershell
# Activation de l'environnement virtuel
.venv\Scripts\activate

# Tests de l'API de Paiement (5 tests)
$env:PYTHONPATH="services/payment-api"
python -m pytest services/payment-api/tests -v

# Tests du Moteur de Remédiation (3 tests)
$env:PYTHONPATH="services/remediation-engine"
python -m pytest services/remediation-engine/tests -v
```
