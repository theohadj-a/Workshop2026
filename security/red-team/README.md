# 🔴 Red Team Attack Suite — PROJECT RESILIENCE-ALPHA

Ce répertoire contient l'outillage offensif utilisé pour la démonstration en live devant le jury.

## 🎯 Objectif de la Démonstration
Prouver que le système peut subir une agression réseau ou applicative réelle initiée depuis un **PC externe** (connecté sur le Wi-Fi `RESILIENCE-G<n>`), détecter la dérive de performance via **AIOps (Isolation Forest)**, et opérer le **Zero-Touch Recovery** sans aucune action humaine.

---

## 🚀 Utilisation depuis le PC Attaquant

### Pré-requis sur le PC Attaquant :
```bash
pip install httpx
```

### 1. Scénario Démo Complet (Recommandé pour la soutenance) :
```bash
python security/red-team/attack.py --host <IP_DU_PC_CIBLE> --port 8000 --mode demo
```
*Effet : Injecte 1200ms de latence et 65% d'erreurs 500, tout en envoyant un flux de transactions réelles pour faire réagir immédiatement l'Isolation Forest.*

### 2. Attaque HTTP Flood (Volumétrique) :
```bash
python security/red-team/attack.py --host <IP_DU_PC_CIBLE> --port 8000 --mode flood --duration 30
```

### 3. Attaque Slowloris (Épuisement de sockets) :
```bash
python security/red-team/attack.py --host <IP_DU_PC_CIBLE> --port 8000 --mode slowloris --duration 30
```
