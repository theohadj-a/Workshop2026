# Déploiement Kubernetes — PROJECT RESILIENCE-ALPHA

Ce répertoire contient l'ensemble des manifestes Kubernetes permettant de déployer la plateforme de paiement en cluster hautement disponible avec réplicas, auto-scaling et politiques de sécurité.

---

## 🏗️ Architecture du Cluster K8s

- **Namespace dédié** : `resilience-alpha`
- **Déploiement `payment-api`** : `replicas: 3` avec sondes de santé `livenessProbe` et `readinessProbe` sur `/health`.
- **Haute Disponibilité & Auto-scaling (HPA)** : mise à l'échelle automatique de 3 à 8 réplicas en cas de pic CPU/latence lors d'une attaque.
- **Déploiement `dashboard-ui`** : `replicas: 2` exposé sur le NodePort `30080`.
- **Cybersécurité (NetworkPolicy)** : isolation stricte du backend, seul le trafic en provenance du dashboard ou des sondes internes est autorisé.

---

## 🚀 Déploiement en 1 Commande

### 1. Activer Kubernetes
- **Option Docker Desktop** : Ouvrez Docker Desktop > Paramètres (*Settings*) > Kubernetes > Cocher *"Enable Kubernetes"* > *Apply & Restart*.
- **Option K3d (Alternative ultra-légère)** :
  ```bash
  k3d cluster create resilience-cluster -p "30080:30080@loadbalancer"
  ```

### 2. Builder les images Docker en local
```bash
docker build -t payment-api:latest services/payment-api
docker build -t dashboard-ui:latest services/dashboard-ui
```

### 3. Appliquer l'ensemble des manifestes
```bash
kubectl apply -f infra/k8s/
```

### 4. Vérifier l'état des pods et services
```bash
kubectl get pods -n resilience-alpha -o wide
kubectl get svc -n resilience-alpha
```

L'interface de paiement et de supervision est alors accessible sur :  
👉 `http://localhost:30080` (ou `http://localhost:3000` en exécution locale).
