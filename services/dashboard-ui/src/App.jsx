import React, { useState, useEffect, useRef } from 'react';
import {
  CreditCard,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Zap,
  Activity,
  Server,
  Lock,
  ArrowRight,
  Terminal,
  Trash2,
  Play,
  Layers,
  Sparkles,
  ShoppingBag,
  ExternalLink,
  Copy,
  Check,
  Flame,
  Radio,
  Sliders,
  CheckSquare
} from 'lucide-react';

export default function App() {
  // Navigation simple par URL native (sans dépendance externe)
  const [currentPath, setCurrentPath] = useState(
    typeof window !== 'undefined' ? window.location.pathname : '/'
  );

  const navigateTo = (path) => {
    if (typeof window !== 'undefined') {
      window.history.pushState({}, '', path);
      setCurrentPath(path);
    }
  };

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const isSupervision = currentPath === '/supervision';

  // État du formulaire de paiement
  const [amount, setAmount] = useState('49.99');
  const [currency, setCurrency] = useState('EUR');
  const [customerName, setCustomerName] = useState('ALEXANDRE MARTIN');
  const [cardNumber, setCardNumber] = useState('4532 8920 1234 5678');
  const [cardExpiry, setCardExpiry] = useState('08/28');
  const [cardCvv, setCardCvv] = useState('789');

  // État de soumission
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastPaymentResult, setLastPaymentResult] = useState(null);
  const [paymentError, setPaymentError] = useState(null);

  // Données de supervision
  const [healthStatus, setHealthStatus] = useState('HEALTHY');
  const [uptime, setUptime] = useState(0);
  const [totalTx, setTotalTx] = useState(0);
  const [transactions, setTransactions] = useState([]);
  const [chaosState, setChaosState] = useState({ is_active: false, latency: 0, error_rate: 0 });
  const [k8sPods, setK8sPods] = useState([]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isRemediating, setIsRemediating] = useState(false);
  const [isChaosLoading, setIsChaosLoading] = useState(false);
  const [actionFeedback, setActionFeedback] = useState(null);

  // Logs et historique
  const [remediationLogs, setRemediationLogs] = useState([]);
  const [remediationHistory, setRemediationHistory] = useState([]);
  const [logFilter, setLogFilter] = useState('ALL');
  const [copiedLogs, setCopiedLogs] = useState(false);
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);

  // Verrou pour éviter les requêtes de polling concurrentes en vol
  const isFetchingRef = useRef(false);

  // Gestion des inputs carte bancaire (chiffres uniquement + espacement automatique)
  const handleCardNumberChange = (e) => {
    const raw = e.target.value.replace(/\D/g, '').slice(0, 16);
    const formatted = raw.match(/.{1,4}/g)?.join(' ') || '';
    setCardNumber(formatted);
  };

  const handleExpiryChange = (e) => {
    const raw = e.target.value.replace(/\D/g, '').slice(0, 4);
    if (raw.length >= 3) {
      setCardExpiry(`${raw.slice(0, 2)}/${raw.slice(2)}`);
    } else {
      setCardExpiry(raw);
    }
  };

  const handleCvvChange = (e) => {
    const raw = e.target.value.replace(/\D/g, '').slice(0, 4);
    setCardCvv(raw);
  };

  const handleNameChange = (e) => {
    setCustomerName(e.target.value.toUpperCase());
  };

  // Détection du type de carte bancaire
  const getCardBrand = (number) => {
    const clean = number.replace(/\s+/g, '');
    if (clean.startsWith('4')) return { name: 'VISA', color: 'from-blue-900 via-indigo-900 to-slate-900' };
    if (/^(5[1-5]|2[2-7])/.test(clean)) return { name: 'MASTERCARD', color: 'from-orange-950 via-red-950 to-slate-900' };
    if (/^3[47]/.test(clean)) return { name: 'AMEX', color: 'from-cyan-950 via-teal-950 to-slate-900' };
    return { name: 'CB', color: 'from-indigo-950 via-slate-900 to-slate-950' };
  };

  const cardBrand = getCardBrand(cardNumber);

  // Fonction helper pour poster un log d'audit
  const postAuditLog = async (level, message, event_id = null) => {
    try {
      await fetch('/remediation/api/v1/remediation/logs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ level, message, event_id }),
      });
    } catch {
      // Ignore silencieusement en cas de coupure réseau
    }
  };

  // Polling optimisé en parallèle (Promise.allSettled) & régulé
  const fetchData = async () => {
    if (isFetchingRef.current) return;
    isFetchingRef.current = true;

    try {
      // 1. Sur la page racine ("/"), on ne vérifie que le healthcheck léger
      if (!isSupervision) {
        try {
          const res = await fetch('/health');
          if (res.ok) {
            const data = await res.json();
            setHealthStatus(data.status);
          } else {
            setHealthStatus('UNHEALTHY');
          }
        } catch {
          setHealthStatus('DOWN');
        }
        return;
      }

      // 2. Sur la page "/supervision", requête groupée en parallèle
      const [healthRes, txRes, chaosRes, logsRes, histRes, podsRes] = await Promise.allSettled([
        fetch('/health'),
        fetch('/api/v1/payments?limit=8'),
        fetch('/api/v1/chaos/status'),
        fetch('/remediation/api/v1/remediation/logs'),
        fetch('/remediation/api/v1/remediation/history'),
        fetch('/remediation/api/v1/remediation/k8s/pods'),
      ]);

      if (healthRes.status === 'fulfilled' && healthRes.value.ok) {
        const hData = await healthRes.value.json();
        setHealthStatus(hData.status);
        setUptime(hData.uptime_seconds || 0);
        setTotalTx(hData.total_transactions || 0);
      } else {
        setHealthStatus('UNHEALTHY');
      }

      if (txRes.status === 'fulfilled' && txRes.value.ok) {
        const tData = await txRes.value.json();
        setTransactions(tData.transactions || []);
      }

      if (chaosRes.status === 'fulfilled' && chaosRes.value.ok) {
        const cData = await chaosRes.value.json();
        setChaosState({
          is_active: Boolean(cData.is_active),
          latency: cData.injected_latency_ms || 0,
          error_rate: cData.injected_error_rate || 0,
        });
      }

      if (logsRes.status === 'fulfilled' && logsRes.value.ok) {
        const lData = await logsRes.value.json();
        setRemediationLogs(lData.logs || []);
      }

      if (histRes.status === 'fulfilled' && histRes.value.ok) {
        const hData = await histRes.value.json();
        setRemediationHistory(hData.history || []);
      }

      if (podsRes.status === 'fulfilled' && podsRes.value.ok) {
        const pData = await podsRes.value.json();
        setK8sPods(pData.pods || []);
      }
    } catch (err) {
      console.warn('Erreur lors du cycle de rafraîchissement SOC', err);
    } finally {
      isFetchingRef.current = false;
    }
  };

  // Intervalle de rafraîchissement espacé (5000ms au lieu de 2000ms, désactivé si onglet en arrière-plan)
  useEffect(() => {
    fetchData();

    if (!autoRefreshEnabled || !isSupervision) return;

    const interval = setInterval(() => {
      if (typeof document !== 'undefined' && document.hidden) return;
      fetchData();
    }, 5000);

    return () => clearInterval(interval);
  }, [isSupervision, autoRefreshEnabled]);

  // Soumission d'une transaction de paiement client
  const handlePayment = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setPaymentError(null);
    setLastPaymentResult(null);

    const cleanCard = cardNumber.replace(/\s+/g, '');
    if (cleanCard.length < 12) {
      setPaymentError("Veuillez saisir un numéro de carte valide à 16 chiffres.");
      setIsSubmitting(false);
      return;
    }

    try {
      const res = await fetch('/api/v1/payments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: parseFloat(amount),
          currency,
          customer_name: customerName,
          customer_email: `${customerName.toLowerCase().replace(/\s+/g, '.')}@example.fr`,
          card_number: cleanCard,
          card_expiry: cardExpiry,
          card_cvv: cardCvv,
          merchant_id: 'MERCHANT-RESILIENCE-01',
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setLastPaymentResult(data);
        postAuditLog('INFO', `[CLIENT PAYMENT] Paiement validé de ${data.amount} ${data.currency} (Réf: ${data.reference})`);
      } else {
        const err = await res.json().catch(() => ({ detail: 'Échec de traitement bancaire' }));
        const errMsg = err.detail || 'Erreur lors de la transaction (Code HTTP 500).';
        setPaymentError(errMsg);
        postAuditLog('ERROR', `[CLIENT PAYMENT REJETÉ] Échec HTTP ${res.status} : ${errMsg}`);
      }
    } catch {
      setPaymentError('Impossible de joindre le service de paiement (Service DOWN ou Bloqué par le WAF)');
      postAuditLog('ERROR', '[CLIENT PAYMENT] Passerelle de paiement inaccessible ou crashée');
    } finally {
      setIsSubmitting(false);
      fetchData();
    }
  };

  // ACTION 1 : Simuler 10 transactions nominales
  const handleSimulateBatch = async () => {
    setIsRefreshing(true);
    setActionFeedback(null);
    try {
      const res = await fetch('/api/v1/payments/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count: 10, currency: 'EUR' }),
      });
      if (res.ok) {
        const data = await res.json();
        const msg = `${data.successful}/10 transactions validées (${data.failed} rejets 500)`;
        setActionFeedback({ type: data.failed > 0 ? 'WARN' : 'SUCCESS', message: msg });
        await postAuditLog(
          data.failed > 0 ? 'WARN' : 'INFO',
          `[TRAFIC BATCH] Lot de 10 transactions injecté : ${data.successful} approuvées, ${data.failed} échecs`
        );
      }
      await fetchData();
    } catch (err) {
      console.error(err);
      setActionFeedback({ type: 'ERROR', message: 'Échec lors de la génération du lot' });
    } finally {
      setIsRefreshing(false);
    }
  };

  // ACTION 2 : Simuler Attaque (Latence + Erreurs 500)
  // Répare le problème : configure le chaos ET envoie immédiatement des requêtes réelles pour produire des erreurs 500 visibles
  const handleTriggerChaos = async () => {
    setIsChaosLoading(true);
    setActionFeedback(null);
    try {
      // 1. Configuration du chaos dans le microservice payment-api
      await fetch('/api/v1/chaos/configure', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ injected_latency_ms: 1200, injected_error_rate: 0.6 }),
      });

      // 2. Émission d'un log d'alerte immédiat
      await postAuditLog(
        'ALERT',
        '[CHAOS ENGINEERING] Injection active : Latence +1200ms, 60% d\'erreurs 500 sur la passerelle'
      );

      // 3. Déclenchement d'un lot de test pour matérialiser les erreurs 500 à l'écran et dans Prometheus
      const simRes = await fetch('/api/v1/payments/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count: 6, currency: 'EUR' }),
      });

      if (simRes.ok) {
        const simData = await simRes.json();
        await postAuditLog(
          'ERROR',
          `[HTTP 500 GATEWAY] Vague d'attaque générée : ${simData.failed}/${simData.requested} requêtes ont échoué avec le code HTTP 500`
        );
        setActionFeedback({
          type: 'ALERT',
          message: `Attaque active : ${simData.failed} erreurs 500 produites ! Le modèle AIOps est alerté.`,
        });
      } else {
        setActionFeedback({ type: 'ALERT', message: 'Chaos configuré (Latence 1.2s, 60% Erreurs 500).' });
      }

      await fetchData();
    } catch (err) {
      console.error(err);
      setActionFeedback({ type: 'ERROR', message: 'Erreur lors de la configuration du chaos' });
    } finally {
      setIsChaosLoading(false);
    }
  };

  // ACTION 3 : Réinitialiser à l'état nominal (Reset Chaos)
  const handleResetChaos = async () => {
    setIsChaosLoading(true);
    setActionFeedback(null);
    try {
      await fetch('/api/v1/chaos/reset', { method: 'POST' });
      await postAuditLog(
        'SUCCESS',
        '[RÉTABLISSEMENT] Chaos désactivé. Latence 0ms, Erreurs 0%. Métriques nominales rétablies.'
      );
      setActionFeedback({ type: 'SUCCESS', message: 'Système rétabli à l\'état nominal (0ms latence, 0% erreur).' });
      await fetchData();
    } catch (err) {
      console.error(err);
    } finally {
      setIsChaosLoading(false);
    }
  };

  // ACTION 4 : Crash immédiat du conteneur (Test Self-Healing K8s natif)
  const handleCrashPod = async () => {
    if (!window.confirm("Êtes-vous sûr de vouloir crasher le processus du pod payment-api ? K8s le relancera automatiquement (CrashLoop / Self-Healing).")) {
      return;
    }
    try {
      await postAuditLog('ALERT', '[CHAOS INFRA] Crash forcé du pod payment-api initié (SIGTERM/exit 1)...');
      await fetch('/api/v1/chaos/crash', { method: 'POST' });
      setActionFeedback({ type: 'ALERT', message: 'Processus payment-api crashé. Sonde K8s en cours de détection...' });
      setTimeout(fetchData, 1500);
    } catch {
      // Ignorer, le pod s'éteint
    }
  };

  // ACTION 5 : Déclencher la remédiation autonome Zero-Touch
  const handleTriggerRemediation = async () => {
    setIsRemediating(true);
    setActionFeedback(null);
    try {
      await postAuditLog('ACTION', '[DEMO SOC] Déclenchement manuel de la remédiation autonome Zero-Touch...');
      const res = await fetch('/remediation/api/v1/remediation/trigger', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: "Déclenchement direct via Console SOC" }),
      });
      // Réinitialise également le chaos en parallèle
      await fetch('/api/v1/chaos/reset', { method: 'POST' }).catch(() => {});

      if (res.ok) {
        setActionFeedback({
          type: 'SUCCESS',
          message: 'Remédiation Zero-Touch terminée : Rollout restart effectué et transaction de test validée !',
        });
      }
      await fetchData();
    } catch (err) {
      console.error(err);
      setActionFeedback({ type: 'ERROR', message: 'Erreur lors du déclenchement de la remédiation' });
    } finally {
      setIsRemediating(false);
    }
  };

  // ACTION 6 : Vider les logs
  const handleClearLogs = async () => {
    try {
      await fetch('/remediation/api/v1/remediation/logs', { method: 'DELETE' });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  // ACTION 7 : Copier les logs dans le presse-papier
  const handleCopyLogs = () => {
    const text = filteredLogs.map((l) => `[${l.time}] [${l.level}] ${l.message}`).join('\n');
    navigator.clipboard.writeText(text);
    setCopiedLogs(true);
    setTimeout(() => setCopiedLogs(false), 2000);
  };

  // Filtrage des logs
  const filteredLogs = remediationLogs.filter((log) => {
    if (logFilter === 'ALL') return true;
    return log.level === logFilter;
  });

  return (
    <div className="min-h-screen bg-[#070A12] text-slate-100 flex flex-col font-sans">
      {/* ========================================================================= */}
      {/* BARRE DE NAVIGATION COMMUNE & SÉLECTEUR D'ÉCOSYSTÈME                     */}
      {/* ========================================================================= */}
      <nav className="border-b border-slate-800/80 bg-[#0A0E1A]/95 backdrop-blur-md sticky top-0 z-50 px-4 md:px-8 py-3">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-3">
          {/* Logo & Switcher de Vue */}
          <div className="flex items-center gap-4 w-full md:w-auto justify-between md:justify-start">
            <div className="flex items-center gap-2.5">
              <div className="p-2 bg-gradient-to-tr from-indigo-600 to-indigo-400 text-white rounded-xl shadow-lg shadow-indigo-600/30">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <span className="font-extrabold tracking-wider text-sm md:text-base text-white flex items-center gap-2">
                  RESILIENCE-ALPHA
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-700/60 uppercase">
                    M2 EPSI 2026
                  </span>
                </span>
                <p className="text-[11px] text-slate-400 hidden sm:block">Zero-Touch Recovery & Cyber-Résilience Autonome</p>
              </div>
            </div>

            {/* Onglets Navigation Inter-Pages */}
            <div className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800">
              <button
                onClick={() => navigateTo('/')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 ${
                  !isSupervision
                    ? 'bg-indigo-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <CreditCard className="w-3.5 h-3.5" />
                <span>Terminal Bancaire</span>
              </button>

              <button
                onClick={() => navigateTo('/supervision')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 ${
                  isSupervision
                    ? 'bg-indigo-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Activity className="w-3.5 h-3.5" />
                <span>Supervision SOC</span>
              </button>
            </div>
          </div>

          {/* Raccourcis Utiles vers l'Écosystème (Docs, Metrics, Attaquant) */}
          <div className="flex items-center gap-2 text-xs font-mono w-full md:w-auto justify-end">
            <a
              href="/docs"
              target="_blank"
              rel="noreferrer"
              className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 flex items-center gap-1 transition"
              title="Documentation interactive Swagger de l'API de Paiement"
            >
              <ExternalLink className="w-3 h-3 text-slate-400" />
              <span>Swagger</span>
            </a>

            <a
              href="/metrics"
              target="_blank"
              rel="noreferrer"
              className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 flex items-center gap-1 transition"
              title="Métriques Prometheus en temps réel"
            >
              <ExternalLink className="w-3 h-3 text-slate-400" />
              <span>Metrics</span>
            </a>

            <a
              href="http://localhost:3001"
              target="_blank"
              rel="noreferrer"
              className="px-2.5 py-1 rounded-lg bg-rose-950/70 hover:bg-rose-900/80 text-rose-300 border border-rose-800/60 flex items-center gap-1 transition font-bold"
              title="Console externe de l'attaquant Red Team (Port 3001)"
            >
              <Flame className="w-3 h-3 text-rose-400" />
              <span>Attaquant</span>
            </a>

            {/* Statut santé global */}
            <div className="ml-2 pl-2 border-l border-slate-800 flex items-center gap-1.5">
              {healthStatus === 'HEALTHY' ? (
                <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/30 text-emerald-400 text-[11px]">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  ONLINE
                </span>
              ) : (
                <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-950/80 border border-rose-500/30 text-rose-400 text-[11px]">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-ping" />
                  INCIDENT
                </span>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* ========================================================================= */}
      {/* VUE 1 : TERMINAL DE PAIEMENT CLIENT ÉPURÉ (ACCESSIBLE SUR "/")            */}
      {/* ========================================================================= */}
      {!isSupervision && (
        <main className="flex-1 max-w-5xl mx-auto w-full p-4 md:p-8 flex flex-col justify-center">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Colonne Gauche : Récapitulatif Commande & Rendu Carte Virtuelle */}
            <div className="lg:col-span-5 space-y-6">
              <div
                className={`relative overflow-hidden w-full h-56 rounded-2xl bg-gradient-to-tr ${cardBrand.color} p-6 shadow-2xl text-white border border-white/10 transition-all duration-500 transform hover:scale-[1.02]`}
              >
                <div className="absolute -top-16 -right-16 w-48 h-48 bg-white/5 rounded-full blur-xl pointer-events-none" />

                <div className="flex justify-between items-start mb-6">
                  <div className="w-12 h-9 bg-gradient-to-br from-amber-200 via-amber-400 to-amber-500 rounded-md border border-amber-300 shadow-md flex items-center justify-center p-1">
                    <div className="w-full h-full border border-amber-700/40 rounded-sm grid grid-cols-2 gap-0.5 opacity-60">
                      <div className="border-r border-amber-700/40" />
                      <div />
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-black tracking-widest text-slate-200">{cardBrand.name}</span>
                    <span className="block text-[9px] text-slate-400 font-mono tracking-wider">RESILIENCE-SECURE</span>
                  </div>
                </div>

                <div className="text-xl md:text-2xl font-mono tracking-widest mb-6 font-semibold drop-shadow-md">
                  {cardNumber || '•••• •••• •••• ••••'}
                </div>

                <div className="flex justify-between items-end text-xs uppercase tracking-wider text-slate-200">
                  <div>
                    <span className="block text-[9px] text-slate-400 font-medium">Titulaire</span>
                    <span className="font-semibold text-white tracking-wide">{customerName || 'NOM DU CLIENT'}</span>
                  </div>
                  <div>
                    <span className="block text-[9px] text-slate-400 font-medium">Expire Fin</span>
                    <span className="font-semibold text-white tracking-wide">{cardExpiry || 'MM/AA'}</span>
                  </div>
                </div>
              </div>

              <div className="bg-[#0F1626] border border-slate-800 rounded-2xl p-5 space-y-3">
                <div className="flex items-center justify-between text-xs text-slate-400 pb-3 border-b border-slate-800">
                  <span className="flex items-center gap-2">
                    <ShoppingBag className="w-4 h-4 text-indigo-400" />
                    Panier Sécurisé
                  </span>
                  <span className="font-mono text-slate-300">#RES-2026-ALPHA</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-300">Pack Sûreté Numérique (Fictif)</span>
                  <span className="font-bold text-white font-mono">
                    {amount} {currency}
                  </span>
                </div>
                <div className="text-[11px] text-slate-400 pt-2 flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>Environnement bac à sable — Protégé par Reverse-Proxy Nginx & WAF.</span>
                </div>
              </div>
            </div>

            {/* Colonne Droite : Formulaire de Paiement */}
            <div className="lg:col-span-7 bg-[#0F1626] border border-slate-800 rounded-2xl p-6 md:p-8 shadow-xl">
              <div className="mb-6">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <span>Informations de Paiement</span>
                </h2>
                <p className="text-xs text-slate-400 mt-1">Saisissez les coordonnées de votre carte de test ci-dessous.</p>
              </div>

              <form onSubmit={handlePayment} className="space-y-4">
                <div className="grid grid-cols-3 gap-3">
                  <div className="col-span-2">
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Montant à payer</label>
                    <div className="relative">
                      <input
                        type="number"
                        step="0.01"
                        min="1"
                        value={amount}
                        onChange={(e) => setAmount(e.target.value)}
                        required
                        className="w-full bg-[#080C15] border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                      />
                      <span className="absolute right-3 top-2.5 text-xs text-slate-400 font-bold">{currency}</span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Presets</label>
                    <div className="flex gap-1.5">
                      {['15', '49.99', '120'].map((p) => (
                        <button
                          key={p}
                          type="button"
                          onClick={() => setAmount(p)}
                          className={`flex-1 py-2 text-xs rounded-lg border font-mono transition ${
                            amount === p
                              ? 'bg-indigo-600/30 border-indigo-500 text-indigo-300 font-bold'
                              : 'bg-slate-900 border-slate-700 text-slate-400 hover:text-white'
                          }`}
                        >
                          {p}€
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Nom du Titulaire</label>
                  <input
                    type="text"
                    value={customerName}
                    onChange={handleNameChange}
                    required
                    placeholder="JEAN DUPONT"
                    className="w-full bg-[#080C15] border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white uppercase tracking-wider focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <div className="flex justify-between items-center mb-1">
                    <label className="text-xs font-semibold text-slate-300">Numéro de Carte Bancaire</label>
                    <span className="text-[10px] text-indigo-400 font-semibold">{cardBrand.name}</span>
                  </div>
                  <div className="relative">
                    <input
                      type="text"
                      inputMode="numeric"
                      value={cardNumber}
                      onChange={handleCardNumberChange}
                      required
                      placeholder="4532 0000 0000 0000"
                      maxLength={19}
                      className="w-full bg-[#080C15] border border-slate-700 rounded-xl pl-10 pr-3.5 py-2.5 text-sm text-white font-mono tracking-widest focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                    />
                    <CreditCard className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Date d'Expiration</label>
                    <input
                      type="text"
                      inputMode="numeric"
                      value={cardExpiry}
                      onChange={handleExpiryChange}
                      required
                      placeholder="MM/AA"
                      maxLength={5}
                      className="w-full bg-[#080C15] border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono tracking-widest text-center focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Code CVV</label>
                    <div className="relative">
                      <input
                        type="text"
                        inputMode="numeric"
                        value={cardCvv}
                        onChange={handleCvvChange}
                        required
                        placeholder="123"
                        maxLength={4}
                        className="w-full bg-[#080C15] border border-slate-700 rounded-xl pl-9 pr-3.5 py-2.5 text-sm text-white font-mono tracking-widest text-center focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                      />
                      <Lock className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-3" />
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full mt-4 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 disabled:opacity-50 text-white font-bold py-3.5 px-4 rounded-xl shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center gap-2 text-sm tracking-wide"
                >
                  {isSubmitting ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Autorisation bancaire en cours...
                    </>
                  ) : (
                    <>
                      <span>Payer {amount} {currency}</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>

              {lastPaymentResult && (
                <div className="mt-6 p-4 rounded-xl bg-emerald-950/70 border border-emerald-500/50 text-emerald-200">
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0 mt-0.5" />
                    <div className="text-xs space-y-1 w-full">
                      <div className="font-bold text-sm text-emerald-300 flex justify-between items-center">
                        <span>Paiement Validé avec Succès !</span>
                        <span className="font-mono text-[11px] bg-emerald-900/80 px-2 py-0.5 rounded text-emerald-200">
                          {lastPaymentResult.status}
                        </span>
                      </div>
                      <div className="text-slate-300">
                        Référence : <span className="font-mono text-white font-semibold">{lastPaymentResult.reference}</span>
                      </div>
                      <div className="text-slate-300">
                        Code Autorisation : <span className="font-mono text-emerald-300 font-bold">{lastPaymentResult.auth_code}</span>
                      </div>
                      <div className="text-[11px] text-slate-400 pt-1 font-mono">
                        Transaction persistée dans PostgreSQL
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {paymentError && (
                <div className="mt-6 p-4 rounded-xl bg-rose-950/70 border border-rose-500/50 text-rose-200">
                  <div className="flex items-start gap-3">
                    <XCircle className="w-6 h-6 text-rose-400 shrink-0 mt-0.5" />
                    <div className="text-xs space-y-1">
                      <div className="font-bold text-sm text-rose-300">Échec de la Transaction</div>
                      <div>{paymentError}</div>
                      <p className="text-slate-400 text-[11px] pt-1">
                        Le système de paiement bancaire rencontre une perturbation (ou une attaque). Le moteur de remédiation autonome Zero-Touch va intervenir sous peu.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </main>
      )}

      {/* ========================================================================= */}
      {/* VUE 2 : CENTRE DE SUPERVISION SOC & CYBER-RÉSILIENCE (SUR "/supervision") */}
      {/* ========================================================================= */}
      {isSupervision && (
        <main className="flex-1 max-w-7xl mx-auto w-full p-4 md:p-8 space-y-6">
          {/* BANDEAU D'ALERTE EN CAS D'INCIDENT / CHAOS ACTIF */}
          {chaosState.is_active && (
            <div className="p-4 rounded-2xl bg-rose-950/90 border-2 border-rose-600 text-rose-200 shadow-2xl shadow-rose-950/80 flex flex-col sm:flex-row items-center justify-between gap-4 animate-pulse">
              <div className="flex items-center gap-3.5">
                <div className="p-2.5 bg-rose-600 text-white rounded-xl">
                  <AlertTriangle className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-extrabold text-white text-sm md:text-base flex items-center gap-2">
                    INCIDENT APPLICATIF ACTIF (CHAOS INJECTÉ)
                    <span className="text-[10px] bg-rose-800 text-rose-100 px-2 py-0.5 rounded-full font-mono uppercase">
                      Score Anormal
                    </span>
                  </h3>
                  <p className="text-xs text-rose-300 mt-0.5">
                    Latence forcée : <strong className="font-mono text-white">{chaosState.latency}ms</strong> | 
                    Taux d'erreurs 500 : <strong className="font-mono text-white">{(chaosState.error_rate * 100).toFixed(0)}%</strong>. 
                    L'agent ML (Isolation Forest) détecte l'écart statistique et alerte le moteur.
                  </p>
                </div>
              </div>

              <button
                onClick={handleResetChaos}
                disabled={isChaosLoading}
                className="px-4 py-2 bg-white text-rose-950 hover:bg-slate-100 font-bold rounded-xl text-xs uppercase tracking-wider shrink-0 transition shadow-lg"
              >
                Rétablir le Flux Nominal
              </button>
            </div>
          )}

          {/* BANDEAU DE FEEDBACK D'ACTION RAPIDE */}
          {actionFeedback && (
            <div
              className={`p-3.5 rounded-xl border text-xs flex items-center justify-between transition ${
                actionFeedback.type === 'SUCCESS'
                  ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-200'
                  : actionFeedback.type === 'ALERT'
                  ? 'bg-rose-950/80 border-rose-500/40 text-rose-200'
                  : 'bg-amber-950/80 border-amber-500/40 text-amber-200'
              }`}
            >
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 shrink-0" />
                <span>{actionFeedback.message}</span>
              </div>
              <button onClick={() => setActionFeedback(null)} className="text-slate-400 hover:text-white text-xs">
                ✕
              </button>
            </div>
          )}

          {/* BANDEAU DE STATISTIQUES SOC CLÉS */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3.5">
            <div className="bg-[#0F1626] border border-slate-800 rounded-xl p-3.5">
              <span className="text-[11px] text-slate-400 block mb-1">Disponibilité Système</span>
              <span
                className={`text-base md:text-lg font-bold font-mono ${
                  healthStatus === 'HEALTHY' ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {healthStatus}
              </span>
            </div>

            <div className="bg-[#0F1626] border border-slate-800 rounded-xl p-3.5">
              <span className="text-[11px] text-slate-400 block mb-1">Uptime Global</span>
              <span className="text-base md:text-lg font-bold font-mono text-white">
                {Math.floor(uptime / 60)}m {Math.round(uptime % 60)}s
              </span>
            </div>

            <div className="bg-[#0F1626] border border-slate-800 rounded-xl p-3.5">
              <span className="text-[11px] text-slate-400 block mb-1">Transactions (PostgreSQL)</span>
              <span className="text-base md:text-lg font-bold font-mono text-indigo-400">{totalTx}</span>
            </div>

            <div className="bg-[#0F1626] border border-slate-800 rounded-xl p-3.5">
              <span className="text-[11px] text-slate-400 block mb-1">Reprise Zero-Touch</span>
              <span className="text-base md:text-lg font-bold font-mono text-amber-400">
                {remediationHistory.length} événement(s)
              </span>
            </div>

            <div className="bg-[#0F1626] border border-slate-800 rounded-xl p-3.5 col-span-2 md:col-span-1">
              <div className="flex justify-between items-center mb-1">
                <span className="text-[11px] text-slate-400">Auto-Refresh (5s)</span>
                <button
                  onClick={() => setAutoRefreshEnabled(!autoRefreshEnabled)}
                  className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold transition ${
                    autoRefreshEnabled ? 'bg-emerald-950 text-emerald-400 border border-emerald-700' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {autoRefreshEnabled ? 'ACTIF' : 'PAUSE'}
                </button>
              </div>
              <button
                onClick={fetchData}
                disabled={isRefreshing}
                className="w-full text-xs py-1 px-2 rounded bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 flex items-center justify-center gap-1.5 transition"
              >
                <RefreshCw className={`w-3 h-3 ${isRefreshing ? 'animate-spin text-indigo-400' : ''}`} />
                <span>Rafraîchir</span>
              </button>
            </div>
          </div>

          {/* TABLEAU DES PODS KUBERNETES EN DIRECT */}
          <div className="bg-[#0F1626] border border-slate-800 rounded-2xl p-5 shadow-xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Server className="w-4 h-4 text-emerald-400" />
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                  Conteneurs & Pods Kubernetes (Namespace: resilience-alpha)
                </h3>
              </div>
              <span className="text-[11px] font-mono text-slate-400">
                {k8sPods.filter((p) => p.is_healthy).length}/{k8sPods.length || 5} pods prêts
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 pt-3">
              {(k8sPods.length > 0
                ? k8sPods
                : [
                    { name: 'payment-api', phase: 'Running', ready: true, restarts: 0, is_healthy: true },
                    { name: 'aiops-detector', phase: 'Running', ready: true, restarts: 0, is_healthy: true },
                    { name: 'remediation-engine', phase: 'Running', ready: true, restarts: 0, is_healthy: true },
                    { name: 'postgres', phase: 'Running', ready: true, restarts: 0, is_healthy: true },
                    { name: 'dashboard-ui', phase: 'Running', ready: true, restarts: 0, is_healthy: true },
                  ]
              ).map((pod, idx) => (
                <div
                  key={pod.name || idx}
                  className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 flex flex-col justify-between space-y-2"
                >
                  <div className="flex items-start justify-between gap-1">
                    <span className="text-[11px] font-mono font-bold text-slate-200 truncate" title={pod.name}>
                      {pod.name.split('-')[0] + '-' + (pod.name.split('-')[1] || '')}
                    </span>
                    <span
                      className={`w-2 h-2 rounded-full shrink-0 ${
                        pod.is_healthy ? 'bg-emerald-400' : 'bg-rose-500 animate-ping'
                      }`}
                    />
                  </div>
                  <div className="flex justify-between items-center text-[10px] text-slate-400 font-mono">
                    <span className={pod.is_healthy ? 'text-emerald-400' : 'text-rose-400'}>{pod.phase}</span>
                    <span>Restarts: {pod.restarts ?? 0}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Colonne Gauche : Commandes de Démonstration Live (5 cols) */}
            <div className="lg:col-span-5 space-y-6">
              <div className="bg-[#0F1626] border border-slate-800 rounded-2xl p-6 shadow-xl">
                <h2 className="text-sm font-bold text-white flex items-center gap-2 mb-4">
                  <Zap className="w-4 h-4 text-amber-400" />
                  Commandes de Démonstration Jury (Live Chaos & Zero-Touch)
                </h2>

                <div className="space-y-3">
                  {/* Commande 1 : Trafic nominal */}
                  <button
                    onClick={handleSimulateBatch}
                    disabled={isRefreshing}
                    className="w-full text-left px-4 py-3 rounded-xl bg-slate-900/80 hover:bg-slate-800/80 border border-slate-700/80 transition flex items-center justify-between"
                  >
                    <div>
                      <div className="text-xs font-semibold text-white">⚡ Générer 10 transactions nominales</div>
                      <div className="text-[11px] text-slate-400">Alimente les métriques Prometheus et le modèle ML</div>
                    </div>
                    <RefreshCw className={`w-4 h-4 text-slate-400 ${isRefreshing ? 'animate-spin' : ''}`} />
                  </button>

                  {/* Commande 2 : Simuler Attaque (Latence + Erreurs 500) */}
                  <button
                    onClick={handleTriggerChaos}
                    disabled={isChaosLoading}
                    className={`w-full text-left px-4 py-3 rounded-xl border transition flex items-center justify-between ${
                      chaosState.is_active
                        ? 'bg-rose-900/60 border-rose-500 text-white shadow-lg shadow-rose-950/50'
                        : 'bg-rose-950/40 hover:bg-rose-900/40 border-rose-700/50 text-rose-300'
                    }`}
                  >
                    <div>
                      <div className="text-xs font-semibold flex items-center gap-1.5">
                        <Flame className="w-3.5 h-3.5 text-rose-400" />
                        <span>Simuler Attaque (Latence 1.2s + 60% Erreurs 500)</span>
                      </div>
                      <div className="text-[11px] text-rose-300/80">
                        {chaosState.is_active
                          ? 'Attaque active — Requêtes 500 générées en continu'
                          : 'Configure le chaos ET produit immédiatement des erreurs 500'}
                      </div>
                    </div>
                    {isChaosLoading ? (
                      <RefreshCw className="w-4 h-4 text-rose-300 animate-spin" />
                    ) : (
                      <AlertTriangle className="w-4 h-4 text-rose-400" />
                    )}
                  </button>

                  {/* Commande 3 : Crash brutal du processus pod */}
                  <button
                    onClick={handleCrashPod}
                    className="w-full text-left px-4 py-3 rounded-xl bg-purple-950/30 hover:bg-purple-900/40 border border-purple-800/50 transition flex items-center justify-between"
                  >
                    <div>
                      <div className="text-xs font-semibold text-purple-300">☠️ Simuler Crash Processus Pod (SIGTERM)</div>
                      <div className="text-[11px] text-purple-400/80">Teste le self-healing automatique Kubernetes natif</div>
                    </div>
                    <Server className="w-4 h-4 text-purple-400" />
                  </button>

                  {/* Commande 4 : Déclenchement manuel de remédiation */}
                  <button
                    onClick={handleTriggerRemediation}
                    disabled={isRemediating}
                    className="w-full text-left px-4 py-3 rounded-xl bg-indigo-950/40 hover:bg-indigo-900/40 border border-indigo-700/50 transition flex items-center justify-between"
                  >
                    <div>
                      <div className="text-xs font-semibold text-indigo-300">🛡️ Déclencher Remédiation Zero-Touch</div>
                      <div className="text-[11px] text-indigo-400/80">Rollout restart K8s + Preuve par transaction test</div>
                    </div>
                    <Play className={`w-4 h-4 text-indigo-400 ${isRemediating ? 'animate-spin' : ''}`} />
                  </button>

                  {/* Commande 5 : Reset nominal */}
                  <button
                    onClick={handleResetChaos}
                    disabled={isChaosLoading}
                    className="w-full text-left px-4 py-3 rounded-xl bg-emerald-950/40 hover:bg-emerald-900/40 border border-emerald-700/50 transition flex items-center justify-between"
                  >
                    <div>
                      <div className="text-xs font-semibold text-emerald-300">🔄 Rétablir Fonctionnement Nominal</div>
                      <div className="text-[11px] text-emerald-400/80">Restaure la latence à 0ms et les erreurs à 0%</div>
                    </div>
                    <CheckSquare className="w-4 h-4 text-emerald-400" />
                  </button>
                </div>
              </div>

              {/* Flux des Dernières Transactions */}
              <div className="bg-[#0F1626] border border-slate-800 rounded-2xl p-6 shadow-xl">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-sm font-bold text-white flex items-center gap-2">
                    <Activity className="w-4 h-4 text-indigo-400" />
                    Dernières Transactions (Persistées PostgreSQL)
                  </h2>
                  <span className="text-[10px] font-mono text-slate-500">{transactions.length} affichée(s)</span>
                </div>

                {transactions.length === 0 ? (
                  <p className="text-xs text-slate-500 py-4 text-center">Aucune transaction enregistrée en base.</p>
                ) : (
                  <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                    {transactions.map((tx) => (
                      <div
                        key={tx.transaction_id}
                        className="p-2.5 rounded-lg bg-slate-900/70 border border-slate-800 flex items-center justify-between text-xs"
                      >
                        <div>
                          <div className="font-semibold text-slate-200">{tx.customer_name}</div>
                          <div className="text-[10px] text-slate-500 font-mono">
                            Carte **** {tx.card_last4} • Réf: {tx.reference}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold text-white">
                            {tx.amount.toFixed(2)} {tx.currency}
                          </div>
                          <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-mono">
                            {tx.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Colonne Droite : Console de Logs et d'Audit Zero-Touch (7 cols) */}
            <div className="lg:col-span-7 bg-[#0F1626] border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <Terminal className="w-5 h-5 text-emerald-400" />
                  <div>
                    <h3 className="text-sm font-bold text-white uppercase tracking-wide">
                      Console d'Audit Zero-Touch & Logs Système
                    </h3>
                    <p className="text-[10px] text-slate-400">Traçabilité complète conforme EBIOS RM, NIS2 & DORA</p>
                  </div>
                </div>

                {/* Actions sur les logs : Copier & Effacer */}
                <div className="flex items-center gap-2 self-end sm:self-auto">
                  <button
                    onClick={handleCopyLogs}
                    className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs flex items-center gap-1 transition"
                    title="Copier les logs affichés dans le presse-papier"
                  >
                    {copiedLogs ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedLogs ? 'Copié !' : 'Copier'}</span>
                  </button>

                  <button
                    onClick={handleClearLogs}
                    title="Réinitialiser le journal de logs"
                    className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Filtres par type de log */}
              <div className="flex flex-wrap items-center gap-1.5 text-[10px] font-mono">
                <span className="text-slate-500 mr-1">Filtres :</span>
                {['ALL', 'ALERT', 'ACTION', 'VERIFY', 'SUCCESS', 'ERROR', 'INFO'].map((f) => (
                  <button
                    key={f}
                    onClick={() => setLogFilter(f)}
                    className={`px-2 py-0.5 rounded transition ${
                      logFilter === f
                        ? 'bg-indigo-600 text-white font-bold'
                        : 'bg-slate-900 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {f === 'ALL' ? `TOUS (${remediationLogs.length})` : f}
                  </button>
                ))}
              </div>

              {/* Écran Terminal Noir avec Défilement */}
              <div className="bg-[#050811] rounded-xl border border-slate-800 p-4 font-mono text-xs max-h-[460px] overflow-y-auto space-y-1.5 shadow-inner">
                {filteredLogs.length === 0 ? (
                  <div className="text-slate-500 text-center py-10">
                    Aucun log pour le filtre sélectionné.
                  </div>
                ) : (
                  filteredLogs.map((log, index) => {
                    let badgeClass = 'bg-slate-800 text-slate-300 border-slate-700';
                    let textClass = 'text-slate-300';

                    if (log.level === 'ALERT') {
                      badgeClass = 'bg-rose-950 text-rose-300 border-rose-800';
                      textClass = 'text-rose-300 font-semibold';
                    } else if (log.level === 'ACTION') {
                      badgeClass = 'bg-indigo-950 text-indigo-300 border-indigo-800';
                      textClass = 'text-indigo-200';
                    } else if (log.level === 'VERIFY') {
                      badgeClass = 'bg-amber-950 text-amber-300 border-amber-800';
                      textClass = 'text-amber-200';
                    } else if (log.level === 'SUCCESS') {
                      badgeClass = 'bg-emerald-950 text-emerald-300 border-emerald-700';
                      textClass = 'text-emerald-300 font-bold';
                    } else if (log.level === 'ERROR') {
                      badgeClass = 'bg-red-900 text-white border-red-700';
                      textClass = 'text-red-400 font-semibold';
                    } else if (log.level === 'WARN') {
                      badgeClass = 'bg-yellow-950 text-yellow-300 border-yellow-800';
                      textClass = 'text-yellow-200';
                    }

                    return (
                      <div
                        key={index}
                        className="flex items-start gap-2.5 leading-relaxed hover:bg-slate-900/60 p-1.5 rounded transition text-[11px]"
                      >
                        <span className="text-slate-500 select-none text-[10px] shrink-0 font-mono">
                          [{log.time}]
                        </span>
                        <span
                          className={`px-1.5 py-0.5 rounded text-[9px] uppercase font-bold shrink-0 border ${badgeClass}`}
                        >
                          {log.level}
                        </span>
                        <span className={`break-all ${textClass}`}>{log.message}</span>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          </div>
        </main>
      )}
    </div>
  );
}
