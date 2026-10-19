# Helm Chart — PROJECT RESILIENCE-ALPHA

Ce répertoire contient le **Helm Chart officiel** (`resilience-alpha`) permettant d'orchestrer, paramétrer et déployer l'intégralité de la plateforme sur n'importe quel cluster Kubernetes (Docker Desktop K8s, K3d, Minikube ou Cloud).

---

## 📦 Structure du Chart

```text
infra/helm/resilience-alpha/
├── Chart.yaml                  # Métadonnées du Chart (v1.0.0)
├── values.yaml                 # Fichier central de configuration (réplicas, ports, ressources)
└── templates/
    ├── _helpers.tpl            # Labels et conventions de nommage
    ├── namespace.yaml          # Namespace dédié (resilience-alpha)
    ├── payment-api-deployment.yaml   # 3 réplicas avec healthchecks
    ├── payment-api-service.yaml      # ClusterIP port 8000
    ├── payment-api-hpa.yaml          # Auto-scaling dynamique (3 à 8 pods)
    ├── dashboard-ui-deployment.yaml  # 2 réplicas frontend React
    ├── dashboard-ui-service.yaml     # NodePort 30080
    ├── remediation-engine-rbac.yaml  # Droits RBAC (ServiceAccount, Role)
    ├── remediation-engine-deployment.yaml # Moteur autonome
    ├── remediation-engine-service.yaml    # Service port 8001
    ├── network-policy.yaml           # Isolation cyber
    └── NOTES.txt               # Instructions post-déploiement
```

---

## 🚀 Utilisation de Helm

### 1. Installer Helm (si nécessaire)
Sur Windows avec Winget :
```powershell
winget install Helm.Helm
```
Ou avec Chocolatey :
```powershell
choco install kubernetes-helm
```

### 2. Déployer la plateforme avec Helm
Depuis la racine du projet (`Code/`) :
```bash
helm install resilience-alpha ./infra/helm/resilience-alpha
```
Ou pour mettre à jour / redéployer dynamiquement :
```bash
helm upgrade --install resilience-alpha ./infra/helm/resilience-alpha
```

### 3. Surcharger des valeurs en ligne de commande
Vous pouvez modifier le nombre de réplicas ou les ressources à la volée sans éditer de fichier :
```bash
# Passer à 5 réplicas pour la démo de haute disponibilité
helm upgrade --install resilience-alpha ./infra/helm/resilience-alpha --set paymentApi.replicaCount=5
```

### 4. Désinstaller la stack
```bash
helm uninstall resilience-alpha
```
