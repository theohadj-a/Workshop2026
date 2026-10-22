# Dashboard & Terminal de Paiement (React + Tailwind)
**PROJECT RESILIENCE-ALPHA — Workshop M2 2026**

Interface utilisateur web moderne pour les transactions bancaires simulées et la supervision en temps réel de la cyber-résilience.

---

## 🎨 Fonctionnalités Principales

1. **Terminal de Paiement Virtuel (Checkout)** :
   - Rendu dynamique d'une carte bancaire avec reflets, puce dorée et badge *RESILIENCE PAY*.
   - Mise à jour instantanée du titulaire et du numéro de carte masqué pendant la frappe.
   - Formulaire de paiement sécurisé (montant, devise EUR/USD, nom, CVV).
   - Validation dynamique : récépissé émeraude avec code d'autorisation `AUTH-XXXXXX` en cas de succès, alerte rouge en cas de panne ou d'attaque.

2. **Bandeau de Supervision Temps Réel** :
   - Statut du système en direct : 🟢 **SYSTÈME OPÉRATIONNEL** / 🔴 **PERTURBATION DÉTECTÉE**.
   - Compteur en direct des transactions globales traitées et temps d'activité (*Uptime*).
   - Indicateur visuel d'état de chaos (latence injectée en millisecondes).

3. **Commandes de Démonstration en 1 Clic** :
   - **⚡ Générer 10 transactions** : envoie une rafale de paiements fictifs pour tester le débit et alimenter le modèle ML.
   - **💥 Simuler Attaque** : injecte 1500 ms de latence et 60% d'erreurs 500 pour provoquer l'incident visible en live.
   - **🔄 Réinitialiser** : rétablit immédiatement les paramètres nominaux.
   - **Flux temps réel** : liste défilante des 8 dernières transactions bancaires enregistrées.

---

## 💻 Développement Local

```bash
# Dans le dossier services/dashboard-ui
npm install
npm run dev
```
L'application démarre sur `http://localhost:3000` avec redirection automatique des requêtes API vers le backend sur `http://localhost:8000`.

## 📦 Build de Production

```bash
npm run build
```
Les fichiers statiques optimisés sont générés dans le dossier `dist/` et servis par Nginx en production.
