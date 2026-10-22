# PROJECT RESILIENCE-ALPHA — Workshop M2 EPSI 2026
> **Équipe :** Théo, Mael, Flora, Fely, Aymeric  
> **Objectif :** Cyber-résilience autonome et reprise sans intervention humaine (*Zero-Touch Recovery*).

---

## 📁 Architecture du Dépôt

```text
Code/
├── docker-compose.yml              # Orchestrateur local des conteneurs (Payment, Remediation, Dashboard, Postgres)
├── .gitignore                      # Exclusions (secrets, venv, bases SQLite, builds)
├── services/
│   ├── payment-api/                # API FastAPI de paiement fictif (PostgreSQL, instrumentée Prometheus)
│   ├── remediation-engine/         # Moteur de reprise autonome (Zero-Touch) relié à K8s & ML
│   ├── auth-service/               # Microservice d'authentification JWT (Supervision SOC & RBAC)
│   └── dashboard-ui/               # Front-end React + Tailwind (Terminal bancaire & Supervision)
├── ai-ops/
│   └── detector/                   # Détecteur d'anomalies ML (Isolation Forest pré-entraîné Scikit-Learn)
├── Attaquant/                      # Module Red Team externe (Dashboard Next.js + Scripts d'attaque)
│   ├── docker-compose.yml          # Lancement autonome du dashboard attaquant
│   ├── Dockerfile                  # Image Node.js 20 Alpine du front attaquant
│   ├── app/                        # Application Next.js (Console cyber-attaque)
│   └── python/                     # Scripts CLI d'attaque volumétrique et dégradation
├── security/
│   └── waf/                        # Reverse Proxy Nginx & filtrage applicatif
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
- 🔐 **Service d'Authentification SOC** : [http://localhost:8002/health](http://localhost:8002/health)

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

---

## 🔴 Console Attaquant & Red Team (Exécution Externe)

Le module **Attaquant** est conçu pour s'exécuter de façon autonome depuis le **PC de l'attaquant** (sur le réseau local ou le point d'accès Wi-Fi de l'exercice), complètement découplé du cluster Kubernetes de défense.

### 📋 Synthèse Complète des Attaques (Aide-Mémoire Soutenance)

| # | Type d'Attaque | Disponible Sur | Commande CLI ou Action Front | Route Cible | Effet Attendu & Réaction Défense | Objectif Démonstration Jury |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Scan OWASP** | 🐍 **Python CLI uniquement** *(sécurité navigateur)* | `python python/attack.py --host <IP> --port 3000 --mode scanner` | `GET /api/v1/payments` *(User-Agent `sqlmap` / `nikto`)* | **Bloqué net par le WAF (HTTP 403 Forbidden)**. Aucune sollicitation du backend. | Prouver l'efficacité du filtrage de réputation et de signature L7. |
| **2** | **HTTP Flood Volumétrique** | 🌐 **Front Web**<br>ou 🐍 **CLI** | Bouton *"Lancer le HTTP Flood"*<br>ou `python python/attack.py --host <IP> --port 3000 --mode flood --duration 20 --threads 15` | `POST /api/v1/payments` | **Rate-limité par le WAF (HTTP 429)** (5 req/s max, burst 10). Si persistant : **Scale HPA Kubernetes** (jusqu'à 8 réplicas). | Démontrer le rate limiting applicatif et l'élasticité horizontale d'infra. |
| **3** | **Slowloris (Connexions lentes)** | 🐍 **Python CLI uniquement** *(sockets TCP bruts)* | `python python/attack.py --host <IP> --port 3000 --mode slowloris --duration 45` | Sockets TCP bruts *(headers partiels keep-alive)* | **Passe le WAF** *(faille volontaire)* ➔ Sature les sockets ➔ **AIOps ML (Isolation Forest) détecte l'explosion de latence** ➔ **Rollout restart Zero-Touch**. | Prouver la détection comportementale L4/L7 par Machine Learning. |
| **4** | **Chaos & Dégradation API** | 🌐 **Front Web**<br>ou 🐍 **CLI** | Bouton *"Appliquer le Chaos"*<br>ou `python python/attack.py --host <IP> --port 3000 --mode chaos` | `POST /api/v1/chaos/configure` | **Passe le WAF** *(requête JSON valide)* ➔ 65% erreurs 500 et 1.2s latence ➔ **L'Isolation Forest signale l'incident** ➔ **Reprise autonome Zero-Touch**. | Démontrer la détection d'une anomalie statistique subtile sans crash physique. |
| **5** | **Crash Brutal du Pod** | 🌐 **Front Web**<br>ou 💻 **cURL** | Bouton *"Crash Fatal"*<br>ou `curl -X POST http://<IP>:3000/api/v1/chaos/crash` | `POST /api/v1/chaos/crash` | Le conteneur se termine brutalement (`exit 1`) ➔ **Pod en CrashLoop** ➔ **Sonde Liveness K8s & surveillance native recréent le pod**. | Démontrer le self-healing automatique face à une panne physique brutale. |
| **6** | **Scénario Démo Clé en Main** | 🐍 **Python CLI** | `python python/attack.py --host <IP> --port 3000 --mode demo` | Enchaîne : Scan ➔ Chaos ➔ Flood | **Enchaînement automatique des 3 niveaux de défense** en 30 secondes. | Présentation fluide et dynamique pour la soutenance orale. |

---

### Démarrage Rapide via Docker Compose

1. **Se positionner dans le dossier de l'attaquant** :
   ```bash
   cd Attaquant
   ```

2. **(Optionnel) Spécifier l'adresse IP de la cible** :
   Par défaut, le dashboard pointe sur `http://localhost:8000`. Si l'API tourne sur un autre PC du réseau :
   ```bash
   # Sur Linux / macOS
   export NEXT_PUBLIC_API_URL="http://<IP_PC_DEFENSEUR>:8000"

   # Sur Windows PowerShell
   $env:NEXT_PUBLIC_API_URL="http://<IP_PC_DEFENSEUR>:8000"
   ```

3. **Lancer le conteneur du Dashboard Attaquant** :
   ```bash
   docker compose up -d --build
   ```

4. **Accéder à l'interface graphique Red Team** :
   - Ouvrez votre navigateur sur [http://localhost:3001](http://localhost:3001).
   - L'interface vous permet de renseigner en direct l'IP et le port de la cible, tester le statut du service (`/health`), et déclencher :
     - **HTTP Flood** : Envoi massif de requêtes concourantes de paiement.
     - **Slowloris** : Saturation des connexions HTTP keep-alive.
     - **Chaos & Latence** : Dégradation artificielle pour forcer le déclenchement de l'AIOps.

Pour arrêter le dashboard attaquant :
```bash
docker compose down
```

### Alternative : Exécution CLI Python directe

Si vous préférez exécuter les attaques en ligne de commande depuis le PC attaquant :
```bash
cd Attaquant
pip install httpx

# Lancer un HTTP Flood vers l'API cible
python python/attack.py --target <IP_PC_DEFENSEUR> --port 8000 --attack flood --duration 30 --threads 15

# Simuler une injection de latence/chaos
python python/attack.py --target <IP_PC_DEFENSEUR> --port 8000 --attack chaos --duration 30
```

---

## 🔐 Sécurisation & Contrôle d'Accès (Monitoring SOC)

Conformément aux exigences de cloisonnement et aux principes **DORA / NIS2** :
- 💳 **Terminal de Paiement (`/`) :** Accessible publiquement sans restriction d'authentification pour simuler un service transactionnel client ouvert.
- 🔴 **Console Attaquant (`Attaquant/`) :** Découplée et sans authentification défensive, simulant un acteur hostile externe.
- 🛡️ **Supervision & Commandes de Remédiation (`/supervision`) :** Strictement protégée par jeton cryptographique **JWT Bearer** délivré par le microservice [`services/auth-service`](services/auth-service).
  - **Profil Administrateur SOC :** `admin` / `socadmin2026!` (Droits de lecture métriques, déclenchement manuel et purge logs).
  - **Profil Analyste SOC :** `operator` / `operator2026!` (Droits de consultation et déclenchement).
