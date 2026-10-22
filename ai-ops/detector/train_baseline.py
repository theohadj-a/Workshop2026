import os
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

def generate_nominal_dataset(n_samples: int = 3000) -> np.ndarray:
    """
    Génère un jeu de données simulant un comportement nominal de la plateforme de paiement :
    - Feature 0 : request_rate (requêtes/sec) -> ~15 ± 5
    - Feature 1 : avg_latency_ms (latence moyenne en ms) -> ~25 ± 10
    - Feature 2 : error_rate_5xx (pourcentage d'erreurs serveur 5xx) -> 0.00 à 0.02 (0 à 2%)
    - Feature 3 : active_requests (requêtes concurrentes) -> ~3 ± 2
    """
    np.random.seed(42)

    request_rate = np.clip(np.random.normal(loc=15.0, scale=4.0, size=n_samples), 1.0, 40.0)
    avg_latency = np.clip(np.random.normal(loc=25.0, scale=8.0, size=n_samples), 5.0, 80.0)
    error_rate = np.clip(np.random.exponential(scale=0.005, size=n_samples), 0.0, 0.03)
    active_requests = np.clip(np.random.normal(loc=3.0, scale=1.5, size=n_samples), 1.0, 10.0)

    dataset = np.column_stack([request_rate, avg_latency, error_rate, active_requests])
    return dataset

def train_and_export_model():
    data_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(data_dir, "model_isolation_forest.joblib")

    print("[ML Train] Génération du jeu de données nominal de référence (3000 observations)...")
    X_train = generate_nominal_dataset()

    print("[ML Train] Entraînement de l'Isolation Forest (n_estimators=100, contamination=0.01)...")
    model = IsolationForest(
        n_estimators=100,
        contamination=0.01,
        random_state=42,
        bootstrap=True,
    )
    model.fit(X_train)

    print(f"[ML Train] Sauvegarde du modèle pré-entraîné dans : {model_path}")
    joblib.dump(model, model_path)

    # Test de validation rapide
    print("\n[ML Test] Validation des prédictions :")
    nominal_sample = np.array([[16.0, 28.0, 0.00, 3.0]])
    attack_sample = np.array([[180.0, 950.0, 0.65, 85.0]])  # Attaque DoS / Saturation

    pred_nom = model.predict(nominal_sample)[0]  # Doit être 1 (Normal)
    pred_att = model.predict(attack_sample)[0]  # Doit être -1 (Anomalie)
    score_nom = model.decision_function(nominal_sample)[0]
    score_att = model.decision_function(attack_sample)[0]

    print(f" - Echantillon Nominal -> Prediction: {pred_nom} (Score: {score_nom:.4f}) {'[OK - Normal]' if pred_nom == 1 else '[FAIL]'}")
    print(f" - Echantillon Attaque -> Prediction: {pred_att} (Score: {score_att:.4f}) {'[OK - Anomalie detectee]' if pred_att == -1 else '[FAIL]'}")
    print("\nModele pre-entraine pret a l'emploi !")

if __name__ == "__main__":
    train_and_export_model()
