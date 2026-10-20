# 🔴 Red Team Attack Console (Standalone Docker)

Console Web interactive et autonome destinée à tourner sur le **PC Attaquant externe** (connecté via le point d'accès Wi-Fi `RESILIENCE-G<n>`).

---

## 🚀 Démarrage en 1 commande sur le PC Attaquant

Placez-vous dans le dossier `security/red-team` et lancez :

```bash
docker compose up -d --build
```

Ouvrez ensuite le navigateur sur :
👉 **`http://localhost:5000`**

---

## 🎯 Fonctionnalités de la Console Attaquant :

1. **Sonde de connectivité en direct (Ping) :**
   * Saisissez l'adresse IP de la machine cible (ex: `192.168.1.50`) et le port (`80`).
   * Cliquez sur **Tester la connectivité** pour valider que le cluster est joignable.

2. **Bouton « Démo Complète Soutenance » (Recommandé Jury) :**
   * Enchaîne l'injection d'anomalie critique (latence 1500ms + erreurs 500) avec une rafale volumétrique de requêtes.
   * Déclenche immédiatement l'AIOps Isolation Forest et la remédiation Zero-Touch sur le SOC.

3. **Attaques spécialisées :**
   * **HTTP Flood** : saturation volumétrique par threads concurrents.
   * **Slowloris** : épuisement silencieux des tables de sockets.

4. **Télémétrie en temps réel :**
   * Compteurs de requêtes envoyées, passées et bloquées par le WAF.
   * Journal d'émission tactique horodaté en direct.
   * Bouton d'arrêt d'urgence.

---

## 🛑 Arrêt :
```bash
docker compose down
```
