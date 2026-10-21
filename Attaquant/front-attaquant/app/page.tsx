"use client";

import React, { useState, useEffect, useRef } from "react";

interface AttackStats {
  sent: number;
  success: number;
  errors: number;
}

interface LogEntry {
  id: string;
  time: string;
  type: "INFO" | "SUCCESS" | "ERROR" | "ATTACK";
  message: string;
}

export default function RedTeamConsole() {
  // Configuration de la cible
  const [targetHost, setTargetHost] = useState<string>("localhost");
  // Port 3000 = WAF Nginx / Dashboard (Port 8000 = Direct API Bypass)`r`n  const [targetPort, setTargetPort] = useState<number>(3000);
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [healthDetails, setHealthDetails] = useState<any>(null);

  // Paramètres d'attaque
  const [duration, setDuration] = useState<number>(15);
  const [concurrency, setConcurrency] = useState<number>(10);
  const [latencyMs, setLatencyMs] = useState<number>(1000);
  const [errorRate, setErrorRate] = useState<number>(0.6);

  // États d'exécution
  const [isAttacking, setIsAttacking] = useState<boolean>(false);
  const [stats, setStats] = useState<AttackStats>({
    sent: 0,
    success: 0,
    errors: 0,
  });
  const [logs, setLogs] = useState<LogEntry[]>([]);

  const logsEndRef = useRef<HTMLDivElement>(null);
  const baseUrl = `http://${targetHost}:${targetPort}`;

  const addLog = (type: LogEntry["type"], message: string) => {
    const time = new Date().toLocaleTimeString();
    setLogs((prev) => [
      { id: Math.random().toString(), time, type, message },
      ...prev.slice(0, 99),
    ]);
  };

  // Vérification de la santé de la cible
  const checkHealth = async () => {
    try {
      const res = await fetch(`${baseUrl}/health`, {
        signal: AbortSignal.timeout(3000),
      });
      const data = await res.json();
      setIsHealthy(res.ok);
      setHealthDetails(data);
    } catch (err) {
      setIsHealthy(false);
      setHealthDetails(null);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, [targetHost, targetPort]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  // Lancement du HTTP Flood réel
  const startHttpFlood = async () => {
    if (isAttacking) return;
    setIsAttacking(true);
    setStats({ sent: 0, success: 0, errors: 0 });
    addLog(
      "ATTACK",
      `Démarrage HTTP Flood (${duration}s, ${concurrency} threads) vers ${baseUrl}`
    );

    let active = true;
    const startTime = Date.now();
    const endTime = startTime + duration * 1000;

    const worker = async () => {
      while (active && Date.now() < endTime) {
        try {
          const payload = {
            amount: Math.round((Math.random() * 50 + 1) * 100) / 100,
            currency: "EUR",
            customer_name: `BOT-${Math.floor(Math.random() * 900 + 100)}`,
            customer_email: "redteam@attack.local",
            card_number: "4532000000009999",
            card_expiry: "12/28",
            card_cvv: "000",
            merchant_id: "TARGET-MERCHANT",
          };

          const res = await fetch(`${baseUrl}/api/v1/payments`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });

          setStats((s) => ({ ...s, sent: s.sent + 1 }));
          if (res.ok) {
            setStats((s) => ({ ...s, success: s.success + 1 }));
          } else {
            setStats((s) => ({ ...s, errors: s.errors + 1 }));
          }
        } catch (err) {
          setStats((s) => ({ ...s, sent: s.sent + 1, errors: s.errors + 1 }));
        }
        await new Promise((r) => setTimeout(r, 50));
      }
    };

    const workers = Array.from({ length: concurrency }, () => worker());
    await Promise.all(workers);

    active = false;
    setIsAttacking(false);
    addLog("INFO", "HTTP Flood terminé.");
  };

  // Injection de Chaos via l'API
  const applyChaos = async () => {
    try {
      addLog(
        "ATTACK",
        `Application du Chaos (Latence: ${latencyMs}ms, Erreurs: ${
          errorRate * 100
        }%)`
      );
      const res = await fetch(`${baseUrl}/api/v1/chaos/configure`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          injected_latency_ms: latencyMs,
          injected_error_rate: errorRate,
        }),
      });
      if (res.ok) {
        addLog("SUCCESS", "Chaos injecté avec succès sur la cible.");
      } else {
        addLog("ERROR", "Échec de la configuration du chaos.");
      }
    } catch (err) {
      addLog("ERROR", `Erreur réseau lors de l'injection du chaos: ${err}`);
    }
  };

  // Réinitialisation du Chaos
  const resetChaos = async () => {
    try {
      const res = await fetch(`${baseUrl}/api/v1/chaos/reset`, {
        method: "POST",
      });
      if (res.ok) {
        addLog(
          "SUCCESS",
          "Paramètres de chaos réinitialisés (Retour nominal)."
        );
      }
    } catch (err) {
      addLog("ERROR", "Impossible de réinitialiser le chaos.");
    }
  };

  // Crash du service
  const triggerCrash = async () => {
    if (!confirm("Voulez-vous vraiment provoquer un crash fatal du service ?"))
      return;
    try {
      addLog("ATTACK", "Envoi de la commande de crash fatal au service...");
      await fetch(`${baseUrl}/api/v1/chaos/crash`, { method: "POST" });
      addLog(
        "SUCCESS",
        "Signal de crash envoyé. Le conteneur devrait redémarrer (Zero-Touch Recovery)."
      );
    } catch (err) {
      addLog("ERROR", "Erreur lors du déclenchement du crash.");
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 font-sans">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* En-tête sobre */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-800 pb-4 gap-4">
          <div>
            <h1 className="text-xl font-semibold tracking-tight text-slate-100">
              Project Resilience-Alpha{" "}
              <span className="text-xs font-mono px-2 py-1 bg-slate-800 rounded text-slate-400 ml-2">
                Red Team Console
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Console d'attaque et d'injection de pannes contrôlées pour test de
              résilience
            </p>
          </div>

          {/* Indicateur de statut cible */}
          <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 px-4 py-2 rounded-lg">
            <div
              className={`w-2.5 h-2.5 rounded-full ${
                isHealthy ? "bg-emerald-500 animate-pulse" : "bg-rose-500"
              }`}
            />
            <div className="text-xs">
              <span className="text-slate-400">Cible : </span>
              <span className="font-mono font-medium text-slate-200">
                {targetHost}:{targetPort}
              </span>
              <span className="ml-2 text-slate-500">
                ({isHealthy ? "En ligne" : "Injoignable"})
              </span>
            </div>
          </div>
        </header>

        {/* Configuration de la cible */}
        <section className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">
              Hôte / IP Cible
            </label>
            <input
              type="text"
              value={targetHost}
              onChange={(e) => setTargetHost(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-slate-600 font-mono"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">
              Port API
            </label>
            <input
              type="number"
              value={targetPort}
              onChange={(e) => setTargetPort(Number(e.target.value))}
              className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-slate-600 font-mono"
            />
          </div>
          <div className="flex items-end h-full pt-5">
            <button
              onClick={checkHealth}
              className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium py-2 rounded transition"
            >
              Vérifier la connectivité
            </button>
          </div>
        </section>

        {/* Grille principale : Contrôles & Statistiques */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Panneau des attaques */}
          <div className="lg:col-span-2 space-y-6">
            {/* Module HTTP Flood */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
              <h2 className="text-sm font-medium text-slate-200 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                Attaque Volumétrique (HTTP Flood)
              </h2>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">
                    Durée (secondes) : {duration}s
                  </label>
                  <input
                    type="range"
                    min="5"
                    max="60"
                    value={duration}
                    onChange={(e) => setDuration(Number(e.target.value))}
                    className="w-full accent-slate-400 bg-slate-950"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">
                    Concurrence (Threads) : {concurrency}
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="30"
                    value={concurrency}
                    onChange={(e) => setConcurrency(Number(e.target.value))}
                    className="w-full accent-slate-400 bg-slate-950"
                  />
                </div>
              </div>

              <button
                onClick={startHttpFlood}
                disabled={isAttacking}
                className={`w-full py-2.5 rounded-lg text-sm font-medium transition ${
                  isAttacking
                    ? "bg-amber-500/20 text-amber-400 border border-amber-500/30 cursor-not-allowed"
                    : "bg-rose-600 hover:bg-rose-500 text-white"
                }`}
              >
                {isAttacking ? "Attaque en cours..." : "Lancer le HTTP Flood"}
              </button>
            </div>

            {/* Module Chaos Engineering */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
              <h2 className="text-sm font-medium text-slate-200 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span>
                Injection de Chaos & Pannes
              </h2>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">
                    Latence injectée : {latencyMs} ms
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="5000"
                    step="100"
                    value={latencyMs}
                    onChange={(e) => setLatencyMs(Number(e.target.value))}
                    className="w-full accent-slate-400 bg-slate-950"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">
                    Taux d'erreurs 500 : {Math.round(errorRate * 100)}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={errorRate}
                    onChange={(e) => setErrorRate(Number(e.target.value))}
                    className="w-full accent-slate-400 bg-slate-950"
                  />
                </div>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  onClick={applyChaos}
                  className="flex-1 bg-purple-600/20 border border-purple-500/30 hover:bg-purple-600/30 text-purple-300 text-xs font-medium py-2 rounded-lg transition"
                >
                  Appliquer le Chaos
                </button>
                <button
                  onClick={resetChaos}
                  className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium py-2 rounded-lg transition"
                >
                  Réinitialiser (Nominal)
                </button>
                <button
                  onClick={triggerCrash}
                  className="bg-rose-950/50 border border-rose-800/50 hover:bg-rose-900/50 text-rose-300 text-xs font-medium px-4 py-2 rounded-lg transition"
                >
                  Crash Fatal
                </button>
              </div>
            </div>
          </div>

          {/* Panneau latéral : Statistiques en direct */}
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
              <h2 className="text-sm font-medium text-slate-200">
                Statistiques de l'attaque
              </h2>

              <div className="space-y-3 font-mono text-sm">
                <div className="flex justify-between bg-slate-950 p-3 rounded border border-slate-800/60">
                  <span className="text-slate-400">Requêtes envoyées :</span>
                  <span className="text-slate-200">{stats.sent}</span>
                </div>
                <div className="flex justify-between bg-slate-950 p-3 rounded border border-slate-800/60">
                  <span className="text-emerald-400">Succès (201) :</span>
                  <span className="text-emerald-400">{stats.success}</span>
                </div>
                <div className="flex justify-between bg-slate-950 p-3 rounded border border-slate-800/60">
                  <span className="text-rose-400">Échecs / Erreurs :</span>
                  <span className="text-rose-400">{stats.errors}</span>
                </div>
              </div>

              {healthDetails && (
                <div className="pt-2 border-t border-slate-800 text-xs text-slate-400 space-y-1">
                  <div>
                    Uptime service :{" "}
                    <span className="font-mono text-slate-200">
                      {healthDetails.uptime_seconds}s
                    </span>
                  </div>
                  <div>
                    Transactions totales :{" "}
                    <span className="font-mono text-slate-200">
                      {healthDetails.total_transactions}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Terminal / Logs épuré */}
        <section className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400">
              Journal d'activité Red Team
            </h3>
            <button
              onClick={() => setLogs([])}
              className="text-xs text-slate-500 hover:text-slate-300 transition"
            >
              Effacer
            </button>
          </div>

          <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 h-48 overflow-y-auto font-mono text-xs space-y-1.5">
            {logs.length === 0 ? (
              <div className="text-slate-600 italic">
                Aucune action enregistrée. En attente d'une attaque...
              </div>
            ) : (
              logs.map((log) => (
                <div key={log.id} className="flex items-start gap-2">
                  <span className="text-slate-500 shrink-0">[{log.time}]</span>
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] uppercase font-semibold shrink-0 ${
                      log.type === "SUCCESS"
                        ? "bg-emerald-950 text-emerald-400 border border-emerald-800/50"
                        : log.type === "ERROR"
                        ? "bg-rose-950 text-rose-400 border border-rose-800/50"
                        : log.type === "ATTACK"
                        ? "bg-amber-950 text-amber-400 border border-amber-800/50"
                        : "bg-slate-800 text-slate-300"
                    }`}
                  >
                    {log.type}
                  </span>
                  <span className="text-slate-300 break-all">
                    {log.message}
                  </span>
                </div>
              ))
            )}
            <div ref={logsEndRef} />
          </div>
        </section>
      </div>
    </div>
  );
}
