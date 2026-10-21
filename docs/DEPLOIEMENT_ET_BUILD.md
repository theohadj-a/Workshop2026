# Guide de Déploiement, Build & Résilience — PROJECT RESILIENCE-ALPHA

## 1. Pipeline de Build Automatisé (Buildx & Kind)

Les scripts [`build-images.bat`](../build-images.bat), [`scripts/build-images.ps1`](../scripts/build-images.ps1) et [`scripts/build-images.sh`](../scripts/build-images.sh) standardisent la chaîne de compilation :

- **Détection d'architecture dynamique :** Détecte l'architecture de la machine hôte (`linux/amd64` sur x86_64, `linux/arm64` sur ARM/Apple Silicon).
- **Contexte isolé :** Exécute `docker buildx build --platform <plateforme> -t <image>:latest --load .` dans le sous-dossier de chaque service.
- **Auto-détection Kind :** Si un cluster Kind est détecté (ex: `kind`), les images compilées y sont automatiquement injectées via `kind load docker-image`. Si aucun cluster n'est actif, le script poursuit sans bloquer.

### Lancer le build :
```powershell
# Windows
.\build-images.bat

# Linux / macOS / WSL
./scripts/build-images.sh
```

---

## 2. Déploiement Kubernetes avec Kind & Ingress

### A. Création du cluster Kind routé (Ports 80/443)
Le fichier [`kind-config.yaml`](../kind-config.yaml) mappe les ports 80 et 443 de la machine hôte vers le nœud Kind :

```powershell
kind create cluster --config kind-config.yaml
```

### B. Déploiement de l'Ingress Controller Nginx
```powershell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=90s
```

### C. Déploiement de la stack applicative via Helm
```powershell
helm upgrade --install resilience-alpha ./infra/helm/resilience-alpha
```

---

## 3. Sécurité & Authentification SOC (Monitoring)

L'accès à la plateforme est cloisonné selon les exigences **DORA / NIS2** :

| Composant | URL | Protection |
| :--- | :--- | :--- |
| **Terminal de Paiement** | `http://localhost/` | **Accès public** (sans authentification). |
| **Supervision SOC** | `http://localhost/supervision` | **Jeton JWT Bearer** émis par `auth-service`. |
| **API Swagger** | `http://localhost/docs` | Accès développeur direct. |
| **Console Attaquant** | `http://localhost:3001` | Module externe autonome (`Attaquant/`). |

### Comptes opérateurs préconfigurés pour la démonstration :
- **Lead SOC (Admin) :** `admin` / `socadmin2026!` *(Lecture métriques, commandes de remédiation, purge logs)*
- **Analyste SOC :** `operator` / `operator2026!` *(Lecture métriques et audit)*

---

## 4. Dépannage & Commandes Utiles

- **Accès direct sans Ingress (Fallback Port-Forward) :**
  ```powershell
  kubectl port-forward -n resilience-alpha svc/dashboard-ui-service 3000:80
  ```
- **Vérifier l'état des Pods :**
  ```powershell
  kubectl get pods -n resilience-alpha
  ```
- **Consulter les journaux du moteur de remédiation :**
  ```powershell
  kubectl logs -n resilience-alpha -l app=remediation-engine --tail=50
  ```
