# Détecteur d'Anomalies AIOps (Machine Learning Clé en Main)
**PROJECT RESILIENCE-ALPHA — Workshop M2 2026**

Module d'intelligence artificielle assurant la détection statistique d'anomalies sur la plateforme de paiement sans utiliser de règles statiques codées en dur.

---

## 🔬 Pourquoi l'Isolation Forest (Scikit-Learn) ?

Contrairement à un simple algorithme conditionnel (`if latency > 1000ms`), l'**Isolation Forest** est un algorithme d'apprentissage non supervisé qui analyse un espace multidimensionnel :

- **Feature 0** : `request_rate` — Nombre de requêtes par seconde
- **Feature 1** : `avg_latency_ms` — Latence moyenne de réponse (en millisecondes)
- **Feature 2** : `error_rate_5xx` — Pourcentage d'erreurs serveur 5xx (0.00 à 1.00)
- **Feature 3** : `active_requests` — Nombre de requêtes concurrentes en vol

### Avantages pour la soutenance :
- **Détection des attaques "Low-and-Slow"** (ex: Slowloris) : le CPU reste bas mais la distribution globale est anormale.
- **Zéro faux positif sur charge légitime** : une montée de requêtes avec des codes 200 est comprise comme un trafic normal.
- **Ultra-léger & Clé en main** : aucun GPU requis, < 30 Mo de RAM, inférence en < 2 millisecondes.

---

## 📁 Fichiers du Module

- **`model_isolation_forest.joblib`** : Le modèle pré-entraîné et sérialisé, prêt à l'emploi.
- **`train_baseline.py`** : Script d'entraînement de la baseline de trafic nominal (3 000 observations synthétiques).
- **`detector.py`** : Agent de surveillance en continu qui consomme les métriques Prometheus, calcule le score d'anomalie et alerte le moteur de remédiation.

---

## 🚀 Utilisation

### 1. Tester une détection instantanée
```powershell
python ai-ops/detector/detector.py --test
```
Résultat attendu :
- Échantillon nominal $\rightarrow$ `Anomalie: False (Score > 0)`
- Échantillon attaque (latence 950ms + 70% erreurs) $\rightarrow$ `Anomalie: True (Score < 0)`

### 2. Lancer la surveillance temps réel
```powershell
python ai-ops/detector/detector.py
```
Le détecteur analyse l'état toutes les 3 secondes. Si 2 anomalies consécutives sont observées, il émet un webhook d'urgence vers `http://localhost:8001/api/v1/remediation/alert`.

### 3. Re-générer le modèle pré-entraîné
```powershell
python ai-ops/detector/train_baseline.py
```
