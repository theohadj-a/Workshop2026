# 📜 Automatisation Infrastructure Ansible — PROJECT RESILIENCE-ALPHA

Ce répertoire contient l'outillage **Infrastructure as Code (IaC)** Ansible pour automatiser le déploiement, la validation et l'audit opérationnel du cluster Kubernetes.

---

## 📁 Structure du Répertoire :

```text
infra/ansible/
├── ansible.cfg                 # Configuration Ansible (stdout YAML, timeouts, privilèges)
├── inventory.ini               # Inventaire des cibles (nœuds K8s, variables globales)
└── playbooks/
    ├── deploy.yml              # Playbook de déploiement complet & validation Helm
    └── healthcheck.yml         # Playbook d'audit de santé des pods et du stockage PVC
```

---

## 🚀 Utilisation :

### 1. Déployer l'intégralité du cluster et valider les rollouts :
```bash
ansible-playbook -i inventory.ini playbooks/deploy.yml
```
* **Actions exécutées :**
  - Vérification de la disponibilité des binaires `kubectl` et `helm`.
  - Contrôle de la connectivité au cluster.
  - Création du namespace `resilience-alpha`.
  - Linting et validation des manifestes Helm.
  - Déploiement et attente du rollout complet (Postgres, Payment API, Remediation Engine).
  - Affichage récapitulatif des ressources en ligne.

### 2. Auditer la santé du cluster et des volumes persistants :
```bash
ansible-playbook -i inventory.ini playbooks/healthcheck.yml
```
* **Actions exécutées :**
  - Contrôle de la phase et du nombre de redémarrages de chaque pod.
  - Validation du statut `Bound` du volume persistant PostgreSQL (PVC).
  - Validation des endpoints de remédiation autonome.
