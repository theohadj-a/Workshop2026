import subprocess
import logging
import json
import os
from typing import List, Dict, Any, Optional
from .config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("K8sManager")

class KubernetesManager:
    def __init__(self, namespace: str = settings.k8s_namespace):
        self.namespace = namespace
        self.k8s_available = self._check_kubectl()

    def _check_kubectl(self) -> bool:
        """Verifie si kubectl est accessible."""
        try:
            res = subprocess.run(
                ["kubectl", "version", "--client", "--output=json"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            return res.returncode == 0
        except Exception:
            logger.warning("kubectl non detecte dans le PATH ou cluster inaccessible.")
            return False

    def get_pods(self, app_label: str = "payment-api") -> List[Dict[str, Any]]:
        """Recupere la liste des pods et leur etat de sante."""
        if not self.k8s_available:
            return []

        try:
            cmd = [
                "kubectl", "get", "pods",
                "-n", self.namespace,
                "-l", f"app={app_label}",
                "-o", "json"
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if res.returncode != 0:
                return []

            data = json.loads(res.stdout)
            pods = []
            for item in data.get("items", []):
                name = item["metadata"]["name"]
                phase = item["status"].get("phase", "Unknown")
                container_statuses = item["status"].get("containerStatuses", [])
                restarts = sum(cs.get("restartCount", 0) for cs in container_statuses)
                ready = all(cs.get("ready", False) for cs in container_statuses) if container_statuses else False

                # Verification d'etat critique (CrashLoopBackOff, OOMKilled, etc.)
                reason = None
                for cs in container_statuses:
                    waiting = cs.get("state", {}).get("waiting", {})
                    if waiting:
                        reason = waiting.get("reason")
                        break

                pods.append({
                    "name": name,
                    "phase": phase,
                    "ready": ready,
                    "restarts": restarts,
                    "reason": reason,
                    "is_healthy": ready and (phase == "Running"),
                })
            return pods
        except Exception as e:
            logger.error(f"Erreur lors de la recuperation des pods: {e}")
            return []

    def restart_unhealthy_pods(self) -> List[str]:
        """Supprime les pods bloques (Error, CrashLoopBackOff) pour forcer K8s a les recreer."""
        pods = self.get_pods()
        restarted = []
        for pod in pods:
            # Si le pod est en erreur ou non-ready avec un probleme detecte
            if not pod["is_healthy"] and pod["reason"] in ("CrashLoopBackOff", "Error", "OOMKilled", "ContainerCannotRun"):
                logger.warning(f"Pod en panne detecte ({pod['name']}) avec motif {pod['reason']}. Suppression pour regeneration...")
                try:
                    subprocess.run(
                        ["kubectl", "delete", "pod", pod["name"], "-n", self.namespace, "--grace-period=0", "--force"],
                        capture_output=True,
                        timeout=5,
                    )
                    restarted.append(pod["name"])
                except Exception as e:
                    logger.error(f"Echec de suppression du pod {pod['name']}: {e}")
        return restarted

    def rollout_restart_deployment(self, deployment_name: str = settings.k8s_deployment) -> bool:
        """Effectue un redemarrage propre et progressif (rolling restart) de l'ensemble des pods."""
        logger.info(f"Declenchement du Rollout Restart sur {deployment_name} dans le namespace {self.namespace}...")
        if not self.k8s_available:
            logger.warning("Mode simulation K8s actif : Rollout restart simule avec succes.")
            return True

        try:
            cmd = ["kubectl", "rollout", "restart", f"deployment/{deployment_name}", "-n", self.namespace]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if res.returncode == 0:
                logger.info(f"Rollout restart applique avec succes: {res.stdout.strip()}")
                return True
            else:
                logger.error(f"Erreur rollout restart: {res.stderr}")
                return False
        except Exception as e:
            logger.error(f"Exception lors du rollout restart: {e}")
            return False

k8s_manager = KubernetesManager()
