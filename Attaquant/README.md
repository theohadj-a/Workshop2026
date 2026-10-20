# PROJECT RESILIENCE-ALPHA — Console Attaquant & Red Team

Ce module regroupe les outils de génération d'attaques cyber et de stress-test applicatif pour évaluer la résilience autonome de la plateforme **Resilience-Alpha**.

> **Note d'architecture :** Ce module s'exécute de façon autonome sur la machine de l'attaquant (PC 2) reliée au réseau local ou au point d'accès Wi-Fi de l'exercice, complètement hors du cluster Kubernetes de défense.

---

## 🚀 Démarrage Rapide (Docker Compose)

### 1. Prérequis
- [Docker & Docker Compose](https://docs.docker.com/get-docker/) installés sur le PC attaquant.

### 2. Configuration & Lancement

Dans ce dossier (`Code/Attaquant`) :

```bash
# 1. (Optionnel) Définir l'URL de l'API de la cible si elle n'est pas sur localhost
# Linux / macOS
export NEXT_PUBLIC_API_URL="http://<IP_PC_DEFENSEUR>:8000"
# Windows PowerShell
$env:NEXT_PUBLIC_API_URL="http://<IP_PC_DEFENSEUR>:8000"

# 2. Démarrer le conteneur du Dashboard Hacker
docker compose up -d --build
```

### 3. Accès Web
- Interface Web : **[http://localhost:3001](http://localhost:3001)**
- Dans l'interface, vous pouvez ajuster l'hôte cible (`targetHost`), le port (`targetPort`), tester le `/health` de l'API cible en un clic et lancer des attaques en direct.

### 4. Arrêt
```bash
docker compose down
```

---

## 🐍 Exécution CLI Directe (Python)

Pour lancer des attaques directement depuis un terminal :

```bash
# Dépendances requises
pip install httpx

# Attaque HTTP Flood (volumétrie forte sur /api/v1/payments)
python python/attack.py --target <IP_PC_DEFENSEUR> --port 8000 --attack flood --duration 30 --threads 20

# Attaque Slowloris (épuisement des sockets HTTP keep-alive)
python python/attack.py --target <IP_PC_DEFENSEUR> --port 8000 --attack slowloris --duration 45

# Injection de Chaos & Latence
python python/attack.py --target <IP_PC_DEFENSEUR> --port 8000 --attack chaos --duration 30
```

---

## 🎯 Scénarios d'Attaque Disponibles

| Type d'Attaque | Cible | Effet Attendu | Réaction Défense |
| :--- | :--- | :--- | :--- |
| **HTTP Flood** | `POST /api/v1/payments` | Pic de requêtes concurrentes, saturation CPU | HPA déclenche le scaling K8s (jusqu'à 10 pods) |
| **Chaos API** | `/health`, `/payments` | Hausse du taux d'erreurs 5xx & latence | AIOps Isolation Forest détecte l'anomalie, remédiation auto |
| **Slowloris** | Socket HTTP (keep-alive) | Consommation des file descriptors | Reverse Proxy / WAF Nginx & redémarrage des pods |
