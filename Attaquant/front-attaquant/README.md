# PROJECT RESILIENCE-ALPHA — Console Attaquant & Guide Red Team

Ce module regroupe la suite d'outils d'offensive et de stress-test applicatif conçue pour évaluer et démontrer la **cyber-résilience autonome** (*Zero-Touch Recovery*) de la plateforme bancaire **Resilience-Alpha**.

> **Note d'architecture réseau :**  
> Ce module est conçu pour s'exécuter de façon autonome depuis le **PC Attaquant externe (PC 2)**, connecté au réseau local ou au point d'accès Wi-Fi de l'exercice (`RESILIENCE-G<n>`), totalement découplé du cluster Kubernetes de défense (PC 1).

---

## 🎯 Architecture des Flux : WAF vs Défense Autonome

Pour démontrer la résilience devant le jury, deux niveaux de défense coexistent :
1. **1ère ligne de défense (WAF Nginx L7) :** Intercepte les attaques conventionnelles évidentes (scanners, bursts bruts).
2. **2ème ligne de défense (AIOps ML & Remédiation Zero-Touch) :** Entre en action lorsque des attaques applicatives plus subtiles (Slowloris, Chaos API) dégradent le service.

```
                          ┌─────────────────────────────┐
                          │    PC ATTAQUANT (RED TEAM)  │
                          └──────────────┬──────────────┘
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   │                                           │
         [Attaques avec WAF]                        [Bypass direct optionnel]
           Port 3000 / 80                                   Port 8000
                   │                                           │
                   ▼                                           ▼
       ┌────────────────────────┐                   ┌────────────────────┐
       │   WAF Nginx L7         │                   │                    │
       │   - 403 (Scanners)     │                   │    payment-api     │
       │   - 429 (Rate Limit)   │                   │     (FastAPI)      │
       │   - Laisse passer      ├──────────────────►│                    │
       │     Slowloris & Chaos  │   Réseau interne  └─────────┬──────────┘
       └────────────────────────┘                               │
                                                                ▼
                                                    ┌────────────────────┐
                                                    │ AIOps ML (IsoFor)  │
                                                    │         +          │
                                                    │ Remédiation K8s    │
                                                    └────────────────────┘
```

---

## 📌 Choix des Ports Cibles

| Port Cible | Description | Utilisation en Démonstration |
| :--- | :--- | :--- |
| **`3000`** *(Docker Compose)*<br>**`80`** / **`30080`** *(Kubernetes)* | **Point d'entrée nominal (WAF Nginx)** | **Cible recommandée pour la démo.** Le flux traverse le WAF. Les scanners sont rejetés (403), le flood est régulé (429), et le Slowloris / Chaos traverse vers le ML. |
| **`8000`** | **Accès direct backend (Bypass WAF)** | Scénario *Shadow IT* ou test direct pour illustrer l'effondrement immédiat de l'API sans la protection du WAF. |

---

## 🚀 Méthode 1 : Interface Web Graphique (Next.js)

### 1. Configuration & Lancement via Docker Compose

Depuis le dossier `Attaquant/` :

```bash
# 1. (Optionnel) Pointer vers l'adresse IP du PC Défenseur
# Linux / macOS :
export NEXT_PUBLIC_API_URL="http://<IP_PC_DEFENSEUR>:3000"

# Windows PowerShell :
$env:NEXT_PUBLIC_API_URL="http://<IP_PC_DEFENSEUR>:3000"

# 2. Démarrer la console Red Team
docker compose up -d --build
```

### 2. Utilisation
1. Ouvrez votre navigateur sur **[http://localhost:3001](http://localhost:3001)**.
2. Indiquez l'IP du PC Défenseur (`targetHost`) et le port (`3000` par défaut).
3. Cliquez sur **« Vérifier la connectivité »** pour valider la liaison avec l'endpoint `/health`.
4. Lancez les attaques en direct :
   - **HTTP Flood :** Ajustez durée et nombre de threads concurrents.
   - **Chaos & Latence :** Injectez 1500 ms de latence et 60 % d'erreurs 500.
   - **Crash Fatal :** Provoque l'extinction forcée du conteneur pour tester le redémarrage K8s / Docker.

Pour arrêter la console :
```bash
docker compose down
```

---

## 🐍 Méthode 2 : Exécution CLI Directe (Script Python)

Le script [`python/attack.py`](python/attack.py) offre une flexibilité totale en ligne de commande :

```bash
# Installation des dépendances légères
pip install httpx
```

### 1. Test du WAF : Détection de Scanners Malveillants (HTTP 403)
Simule une sonde avec un User-Agent de scanner connu (`sqlmap`, `nikto`). Prouve au jury que le WAF est actif :
```bash
python python/attack.py --target <IP_PC_DEFENSEUR> --port 3000 --attack scanner
```
*Résultat attendu :* `HTTP 403 Forbidden - Blocked by Resilience WAF Rule: Malicious User-Agent detected`.

### 2. Attaque HTTP Flood (Saturation de requêtes concourantes)
Envoie une rafale de paiements vers `POST /api/v1/payments` :
```bash
python python/attack.py --target <IP_PC_DEFENSEUR> --port 3000 --attack flood --duration 30 --threads 20
```
*Résultat attendu :* Le WAF autorise le burst initial puis rate-limite le surplus à 5 req/s (HTTP 429 Too Many Requests). Si le volume dépasse le seuil CPU du pod, le HPA Kubernetes active l'auto-scaling.

### 3. Attaque Slowloris (Épuisement des descripteurs de connexion)
Ouvre 80 sockets TCP et maintient des connexions HTTP partielles :
```bash
python python/attack.py --target <IP_PC_DEFENSEUR> --port 3000 --attack slowloris --duration 45
```
*Résultat attendu :* Les connexions saturent le pool. L'API devient inaccessible ou lente. **Le modèle ML AIOps détecte l'explosion de latence et déclenche la remédiation automatique.**

### 4. Injection de Chaos Applicatif (Dégradation furtive)
Configure une anomalie statistique sans volumétrie brute :
```bash
python python/attack.py --target <IP_PC_DEFENSEUR> --port 3000 --attack chaos
```
*Résultat attendu :* L'API commence à renvoyer 65 % d'erreurs 500 et 1200 ms de latence. L'Isolation Forest ML signale l'incident et déclenche un `rollout restart` du déploiement.

### 5. Scénario Démo Complet (Enchaînement automatique)
```bash
python python/attack.py --target <IP_PC_DEFENSEUR> --port 3000 --mode demo
```

---

## 📊 Matrice des Scénarios d'Attaque & Réactions

| Vecteur d'Attaque | Cible | Effet Attendu | Réaction Défensive | Niveau de Preuve |
| :--- | :--- | :--- | :--- | :--- |
| **Scanner OWASP** | `/api/v1/payments` (User-Agent suspect) | Tentative de cartographie de failles | **Bloqué net par le WAF (HTTP 403)** | Conformité WAF / ANSSI |
| **HTTP Flood** | `POST /api/v1/payments` | Pic volumétrique, saturation CPU | **Rate limiting WAF (HTTP 429)** + **Scale HPA K8s (jusqu'à 8 réplicas)** | Résilience élastique |
| **Slowloris** | Sockets HTTP Keep-Alive | Épuisement des descripteurs de sockets | **Passe le WAF** (faille de démonstration) ➔ **AIOps ML détecte la panne** ➔ **Restart Pod** | Détection d'anomalie L4/L7 |
| **Chaos API** | `POST /api/v1/chaos/configure` | Latence artificielle (1.2s) & 65% HTTP 500 | **Passe le WAF** ➔ **Isolation Forest AIOps alerte** ➔ **Reprise autonome Zero-Touch** | Détection comportementale ML |
| **Crash Fatal** | `POST /api/v1/chaos/crash` | Extinction du conteneur API (`exit 1`) | **Pod K8s CrashLoop** ➔ **Remédiation K8s / Liveness probe force le restart** | Reprise sur panne physique |

---

## 🔍 Validation du Rétablissement (Preuve par la Transaction)

Dès que la remédiation automatique se termine, le moteur de remédiation émet un paiement réel d'intégrité :
- Transaction certifiée avec reçu bancaire et statut `SUCCESS`.
- Le résultat s'affiche en temps réel sur le dashboard SOC ([`http://localhost:3000/supervision`](http://localhost:3000/supervision)).
