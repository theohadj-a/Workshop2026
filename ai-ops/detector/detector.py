import os
import sys
import time
import json
import logging
import argparse
import joblib
import numpy as np
import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [AIOps-Detector] %(message)s",
)

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_isolation_forest.joblib")
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
PAYMENT_API_URL = os.getenv("PAYMENT_API_URL", "http://localhost:8000")
REMEDIATION_WEBHOOK_URL = os.getenv("REMEDIATION_WEBHOOK_URL", "http://localhost:8001/api/v1/remediation/alert")
CHECK_INTERVAL_SEC = float(os.getenv("CHECK_INTERVAL_SEC", "3.0"))

class AnomalyDetector:
    def __init__(self, model_path: str = MODEL_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modele ML introuvable a l'emplacement : {model_path}. Lancez train_baseline.py d'abord.")
        logging.info(f"Chargement du modele pre-entraine : {model_path}")
        self.model = joblib.load(model_path)
        self.client = httpx.Client(timeout=2.0)
        self.consecutive_anomalies = 0
        self.last_alert_time = 0.0
        self.prev_req_count = None
        self.prev_error_count = None
        self.prev_timestamp = None

    def extract_metrics(self) -> np.ndarray:
        """
        Extrait les signaux d'observabilite (soit depuis Prometheus, soit directement depuis /metrics).
        Calcule un vrai taux par seconde (delta entre deux collectes).
        """
        now = time.time()
        try:
            # Requete vers l'endpoint /metrics de l'API de paiement
            res = self.client.get(f"{PAYMENT_API_URL}/metrics")
            if res.status_code != 200:
                # Si l'API renvoie une erreur HTTP, c'est deja un signal critique
                return np.array([[0.0, 5000.0, 1.0, 50.0]])

            text = res.text
            # Parsing des metriques Prometheus
            req_count = 0.0
            error_count = 0.0
            active_req = 0.0
            total_duration = 0.0
            total_duration_count = 0.0

            for line in text.splitlines():
                if line.startswith("#"):
                    continue
                if "payment_http_requests_total" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        val = float(parts[-1])
                        req_count += val
                        if 'status_code="5' in line or 'status_code="4' in line:
                            error_count += val
                elif "payment_active_requests" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        active_req = float(parts[-1])
                elif "payment_http_request_duration_seconds_sum" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        total_duration += float(parts[-1])
                elif "payment_http_request_duration_seconds_count" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        total_duration_count += float(parts[-1])

            # Estimation de la latence moyenne en ms
            avg_latency_ms = (total_duration / total_duration_count * 1000.0) if total_duration_count > 0 else 25.0

            # Calcul du debit reel en req/s (delta)
            if self.prev_timestamp is not None and self.prev_req_count is not None:
                dt = max(now - self.prev_timestamp, 0.1)
                delta_req = max(req_count - self.prev_req_count, 0.0)
                delta_err = max(error_count - self.prev_error_count, 0.0)
                request_rate = delta_req / dt
                error_rate = (delta_err / delta_req) if delta_req > 0 else 0.0
            else:
                # Première passe (initialisation)
                request_rate = 15.0  # Valeur nominale par défaut
                error_rate = (error_count / req_count) if req_count > 0 else 0.0

            self.prev_req_count = req_count
            self.prev_error_count = error_count
            self.prev_timestamp = now

            return np.array([[request_rate, avg_latency_ms, error_rate, active_req]])

        except Exception as e:
            # En cas de timeout ou crash de l'API : signal d'anomalie extreme
            logging.warning(f"Impossible de joindre l'API paiement : {e}. Signal critique.")
            return np.array([[0.0, 8000.0, 1.0, 80.0]])

    def evaluate(self, metrics: np.ndarray) -> tuple[bool, float]:
        """
        Evalue le vecteur de metriques via l'Isolation Forest.
        Retourne (is_anomaly, anomaly_score).
        """
        prediction = self.model.predict(metrics)[0]  # 1 = Normal, -1 = Anomalie
        score = float(self.model.decision_function(metrics)[0])
        is_anomaly = (prediction == -1)
        return is_anomaly, score

    def notify_remediation(self, metrics: np.ndarray, score: float):
        """Envoie une alerte automatique au moteur de remediation pour declencher la reprise."""
        now = time.time()
        # Anti-spam d'alertes : max 1 alerte toutes les 15 secondes
        if now - self.last_alert_time < 15.0:
            return

        self.last_alert_time = now
        payload = {
            "source": "AIOps-IsolationForest",
            "timestamp": now,
            "anomaly_score": score,
            "metrics": {
                "request_rate": float(metrics[0][0]),
                "avg_latency_ms": float(metrics[0][1]),
                "error_rate_5xx": float(metrics[0][2]),
                "active_requests": float(metrics[0][3]),
            },
            "recommended_action": "RESTART_OR_FAILOVER",
        }

        logging.critical(f"[ALERTE MACHINE LEARNING] Anomalie confirmee (Score: {score:.4f}) ! Envoi au moteur de remediation...")
        try:
            self.client.post(REMEDIATION_WEBHOOK_URL, json=payload, timeout=2.0)
            logging.info("[AIOps] Signal de reprise envoye avec succes au moteur de remediation.")
        except Exception as e:
            logging.warning(f"[AIOps] Moteur de remediation non joignable ({e}).")

    def run_loop(self):
        logging.info("Demarrage de la boucle de surveillance AIOps temps reel...")
        while True:
            metrics = self.extract_metrics()
            is_anomaly, score = self.evaluate(metrics)

            if is_anomaly:
                self.consecutive_anomalies += 1
                logging.warning(
                    f"[ANOMALIE DETECTEE] (Score: {score:.4f}) "
                    f"Latence={metrics[0][1]:.1f}ms, Erreurs={metrics[0][2]*100:.1f}%, Actifs={metrics[0][3]:.0f} "
                    f"(Occurrences={self.consecutive_anomalies})"
                )
                if self.consecutive_anomalies >= 2:
                    self.notify_remediation(metrics, score)
            else:
                self.consecutive_anomalies = 0
                logging.info(f"[NOMINAL] Score: {score:.4f} | Latence: {metrics[0][1]:.1f}ms | Erreurs: {metrics[0][2]*100:.1f}%")

            time.sleep(CHECK_INTERVAL_SEC)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AIOps Anomaly Detector")
    parser.add_argument("--test", action="store_true", help="Tester une deduction instantanee")
    args = parser.parse_args()

    detector = AnomalyDetector()

    if args.test:
        print("\n--- TEST NOMINAL ---")
        norm_metrics = np.array([[15.0, 25.0, 0.0, 2.0]])
        is_anom, score = detector.evaluate(norm_metrics)
        print(f"Metrics: {norm_metrics} -> Anomalie: {is_anom}, Score: {score:.4f}")

        print("\n--- TEST ATTAQUE (Latence 900ms + Erreurs 500) ---")
        att_metrics = np.array([[120.0, 950.0, 0.70, 75.0]])
        is_anom, score = detector.evaluate(att_metrics)
        print(f"Metrics: {att_metrics} -> Anomalie: {is_anom}, Score: {score:.4f}")
    else:
        detector.run_loop()
