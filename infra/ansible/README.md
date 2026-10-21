# 📜 Automatisation Infrastructure Ansible — PROJECT RESILIENCE-ALPHA

Ce répertoire contient l'outillage **Infrastructure as Code (IaC)** Ansible pour automatiser le déploiement, la validation de conformité et l'audit opérationnel du cluster Kubernetes.

---

## 🎯 Rôle d'Ansible dans l'Architecture

Ansible intervient comme orchestrateur d'infrastructure de haut niveau :
- **Idempotence & Validation :** Vérifie la présence des outils (`kubectl`, `helm`), le linting des manifestes et la création des namespaces.
- **Rollout Progressif :** Déploie la stack Helm et s'assure que chaque microservice (`postgres`, `payment-api`, `auth-service`, `remediation-engine`, `dashboard-ui`) atteint l'état `Running` avant de valider l'étape.
- **Audit de Santé & Résilience :** Le playbook `healthcheck.yml` interroge l'état des pods en JSON, vérifie que le volume persistant PostgreSQL (PVC) est `Bound`, et certifie la disponibilité opérationnelle.

---

## 📁 Structure du Répertoire

```text
infra/ansible/
├── ansible.cfg                 # Paramètres globaux (stdout YAML lisible, timeouts)
├── inventory.ini               # Cibles locales et variables globales (namespace, chart)
├── playbooks/
│   ├── deploy.yml              # Déploiement complet Helm & attente des rollouts K8s
│   └── healthcheck.yml         # Contrôle d'intégrité, audit PVC et état des pods
└── README.md                   # Guide d'exécution et d'intégration
```

---

## 🚀 Comment Lancer les Playbooks

Comme Ansible Control Node s'exécute nativement sous Linux/Unix, vous avez deux méthodes directes sous Windows :

### Méthode 1 : Via WSL2 (Ubuntu) — *Recommandé en local*

```bash
# Dans Ubuntu WSL2 :
sudo apt update && sudo apt install -y ansible

# Se positionner dans le dossier ansible :
cd /mnt/c/Users/HadjKaneki/PROG/cours/Workshop/Code/Workshop2026/infra/ansible

# 1. Déploiement complet de la stack :
ansible-playbook -i inventory.ini playbooks/deploy.yml

# 2. Audit de santé opérationnel du cluster :
ansible-playbook -i inventory.ini playbooks/healthcheck.yml
```

---

### Méthode 2 : Via Conteneur Docker (Sans rien installer sur l'hôte)

```powershell
# Depuis PowerShell à la racine du projet :
docker run --rm -it `
  -v ${PWD}:/work `
  -v ${HOME}/.kube:/root/.kube:ro `
  -w /work/infra/ansible `
  willhallonline/ansible:latest `
  ansible-playbook -i inventory.ini playbooks/healthcheck.yml
```

---

### Méthode 3 : Dans une chaîne CI/CD (GitLab CI / GitHub Actions)

Dans un pipeline d'intégration continue, le runner Linux exécute directement :
```yaml
deploy-k8s:
  stage: deploy
  image: alpine/ansible:latest
  script:
    - ansible-playbook -i infra/ansible/inventory.ini infra/ansible/playbooks/deploy.yml
```
