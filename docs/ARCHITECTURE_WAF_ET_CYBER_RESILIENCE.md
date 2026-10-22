# PROJECT RESILIENCE-ALPHA — Architecture WAF & Cyber-Résilience

> **Document de référence technique :** Articulation entre filtrage WAF Nginx, détection Machine Learning (AIOps) et remédiation Zero-Touch.

---

## 1. Contexte & Démarche de Conception

Dans le cadre du Workshop M2 EPSI *Resilience-Alpha*, l'objectif fondamental du système n'est pas uniquement d'être un bouclier statique, mais de démontrer une **cyber-résilience autonome (*Zero-Touch Recovery*)** face à des incidents ou des attaques capables de dégrader le service.

Pour cette raison, la posture de sécurité applicative est sciemment calibrée en **défense en profondeur à double détente** :
1. **Couche de Prévention WAF (Nginx L7) :** Filtre les menaces évidentes (scanners automatisés OWASP, bursts volumétriques non sollicités sur les endpoints sensibles).
2. **Couche de Cyber-Résilience (ML AIOps & Remédiation K8s) :** Prend en charge les attaques plus sournoises ou les pannes applicatives (Slowloris, Chaos API, fuite de ressources) afin de détecter l'asphyxie et de rétablir automatiquement le système sans intervention humaine.

---

## 2. Cartographie des Flux Réseau & Étanchéité

### Analyse des points d'accès

| Service | Port Interne | Port Hôte Docker Compose | Service Kubernetes | Rôle Réseau |
| :--- | :--- | :--- | :--- | :--- |
| **`dashboard-ui` (WAF)** | `80` | `3000:80` | `NodePort 30080` / `Ingress 80` | **Point d'entrée unique public.** Héberge le WAF Nginx et la SPA React. |
| **`payment-api`** | `8000` | `127.0.0.1:8000:8000` *(debug local)* | `ClusterIP` privé | Accessible uniquement via le réseau interne `resilience-net` / `NetworkPolicy`. |
| **`auth-service`** | `8002` | `127.0.0.1:8002:8002` *(debug local)* | `ClusterIP` privé | Accessible uniquement via Nginx WAF sur `/api/v1/auth/`. |
| **`remediation-engine`** | `8001` | `127.0.0.1:8001:8001` *(debug local)* | `ClusterIP` privé | Pilotage K8s & orchestration de la reprise. |

> [!IMPORTANT]
> **Correction de la brèche WAF Bypass :**  
> Initialement, `payment-api` et `auth-service` étaient exposés publiquement sur `0.0.0.0:8000` et `0.0.0.0:8002`, ce qui permettait à n'importe quel attaquant distant sur le réseau local ou Wi-Fi de contourner intégralement le WAF.  
> Désormais, ces ports sont restreints à `127.0.0.1` pour le diagnostic local des développeurs. Toute machine externe (dont le PC Attaquant Red Team) doit obligatoirement entrer par le port `3000` (Compose) ou `80`/`30080` (K8s) et subir l'inspection du WAF.

---

## 3. Configuration & Règles WAF Nginx

Les configurations ont été alignées sur 3 fichiers synchronisés :
- [`services/dashboard-ui/nginx.conf`](../services/dashboard-ui/nginx.conf) (Image Docker de production)
- [`security/waf/nginx-waf.conf`](../security/waf/nginx-waf.conf) (Fichier de référence WAF)
- [`infra/helm/resilience-alpha/templates/dashboard-ui-configmap.yaml`](../infra/helm/resilience-alpha/templates/dashboard-ui-configmap.yaml) (Déploiement Helm/Kubernetes)

### A. Filtrage des Scanners & Malicious User-Agents (OWASP Top 10)
```nginx
map $http_user_agent $bad_bot {
    default 0;
    ~*(nikto|sqlmap|nmap|dirbuster|gobuster|wprecon) 1;
}

if ($bad_bot) {
    return 403 "Blocked by Resilience WAF Rule: Malicious User-Agent detected\n";
}
```
- **Action :** Tout outil de scan ou sonde automatisée connue est immédiatement rejeté avec un code **HTTP 403 Forbidden**.
- **Preuve soutenance :** `python attack.py --attack scanner` valide cette règle en direct.

### B. Rate Limiting Sélectif (Protection anti-Brute-Force & Flood)
```nginx
limit_req_zone $binary_remote_addr zone=waf_payment_limit:10m rate=5r/s;
limit_req_zone $binary_remote_addr zone=waf_api_limit:10m rate=15r/s;

location /api/v1/payments {
    limit_req zone=waf_payment_limit burst=10 nodelay;
    limit_req_status 429;
    proxy_pass http://resilience-payment-api:8000/api/v1/payments;
    ...
}
```
- **Action :** Les requêtes de paiement bancaire sont plafonnées à 5 requêtes par seconde par adresse IP (avec un burst toléré de 10 requêtes). Au-delà, Nginx renvoie un **HTTP 429 Too Many Requests** sans solliciter le backend.

### C. En-têtes HTTP de Durcissement (Recommandations ANSSI)
```nginx
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
```

---

## 4. Matrice Red Team vs Blue Team (Scénarios d'Attaque)

| Scénario Red Team | Outil / Route | Comportement WAF | Comportement Résilience | Objectif Démonstration |
| :--- | :--- | :--- | :--- | :--- |
| **1. Scan de vulnérabilités** | `attack.py --attack scanner` | **Bloqué net (HTTP 403)** | Aucune sollicitation du backend | Prouver la conformité WAF active |
| **2. HTTP Flood volumétrique** | `attack.py --attack flood` (sur `/api/v1/payments`) | **Rate-limité (HTTP 429)** | Si le burst fait grimper le CPU, le HPA K8s scale le nombre de pods | Démontrer l'élasticité d'infrastructure |
| **3. Slowloris (Connexions lentes)** | `attack.py --attack slowloris` (Sockets TCP partiels) | **Passe le WAF** *(Faille volontaire de démo)* | Les descripteurs saturent ➔ L'AIOps ML détecte la hausse de latence ou l'indisponibilité ➔ Déclenchement de la remédiation autonome | Démontrer la détection L4/L7 par Machine Learning |
| **4. Chaos & Dégradation API** | `attack.py --attack chaos` (sur `/api/v1/chaos/configure`) | **Passe le WAF** *(Requête applicative JSON valide)* | 65% d'erreurs 500 et 1200ms de latence ➔ L'Isolation Forest signale l'incident ➔ `rollout restart` du pod | Démontrer la détection d'anomalie statistique subtile |
| **5. Crash Fatal** | `POST /api/v1/chaos/crash` | **Passe le WAF** | Le conteneur se termine (`exit 1`) ➔ Sondes K8s (Liveness) ou script de supervision relancent le conteneur | Démontrer la reprise sur crash physique |

---

## 5. Déroulement Idéal de la Démonstration (Soutenance)

1. **Phase 1 : Le WAF en action**
   - Lancer un scan rapide avec User-Agent suspect : `python attack.py --attack scanner`.
   - Constater le retour immédiat `HTTP 403 Forbidden` dans les logs Nginx.
2. **Phase 2 : L'attaque volumétrique régulée**
   - Déclencher le HTTP Flood depuis le dashboard Hacker ([`http://localhost:3001`](http://localhost:3001)).
   - Constater que les 10 premières requêtes passent, puis que le WAF renvoie des `429 Too Many Requests`.
3. **Phase 3 : L'incident non filtrable et la résilience autonome (*Zero-Touch*)**
   - Déclencher l'attaque **Chaos** ou **Slowloris**.
   - Observer sur le dashboard de Supervision ([`http://localhost:3000/supervision`](http://localhost:3000/supervision)) :
     - Le voyant passe à l'orange/rouge (*Perturbation détectée*).
     - Les logs affichent l'alerte émise par l'AIOps Isolation Forest.
     - Le Moteur de Remédiation ordonne le redémarrage propre du service.
     - Un paiement de certification est émis automatiquement avec succès.
