import React, { useState, useEffect } from 'react';
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
  ArrowRight
} from 'lucide-react';

export default function App() {
  // État du formulaire de paiement
  const [amount, setAmount] = useState('49.99');
  const [currency, setCurrency] = useState('EUR');
  const [customerName, setCustomerName] = useState('Alexandre Martin');
  const [cardNumber, setCardNumber] = useState('4532 8920 1234 5678');
  const [cardExpiry, setCardExpiry] = useState('08/28');
  const [cardCvv, setCardCvv] = useState('789');

  // État de l'application
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastPaymentResult, setLastPaymentResult] = useState(null);
  const [paymentError, setPaymentError] = useState(null);

  // Données de supervision
  const [healthStatus, setHealthStatus] = useState('HEALTHY');
  const [uptime, setUptime] = useState(0);
  const [totalTx, setTotalTx] = useState(0);
  const [transactions, setTransactions] = useState([]);
  const [chaosState, setChaosState] = useState({ is_active: false, latency: 0, error_rate: 0 });
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Polling des données de santé et des transactions
  const fetchData = async () => {
    try {
      // 1. Health
      const healthRes = await fetch('/health');
      if (healthRes.ok) {
        const data = await healthRes.json();
        setHealthStatus(data.status);
        setUptime(data.uptime_seconds);
        setTotalTx(data.total_transactions);
      } else {
        setHealthStatus('UNHEALTHY');
      }
    } catch {
      setHealthStatus('DOWN');
    }

    try {
      // 2. Transactions
      const txRes = await fetch('/api/v1/payments?limit=8');
      if (txRes.ok) {
        const data = await txRes.json();
        setTransactions(data.transactions || []);
      }
    } catch (e) {
      console.warn("Erreur chargement transactions", e);
    }

    try {
      // 3. Chaos status
      const chaosRes = await fetch('/api/v1/chaos/status');
      if (chaosRes.ok) {
        const cData = await chaosRes.json();
        setChaosState(cData);
      }
    } catch (e) {
      console.warn("Erreur chargement chaos status", e);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 2500);
    return () => clearInterval(interval);
  }, []);

  // Soumission d'une transaction fictive
  const handlePayment = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setPaymentError(null);
    setLastPaymentResult(null);

    try {
      const res = await fetch('/api/v1/payments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: parseFloat(amount),
          currency,
          customer_name: customerName,
          customer_email: `${customerName.toLowerCase().replace(' ', '.')}@example.fr`,
          card_number: cardNumber.replace(/\s+/g, ''),
          card_expiry: cardExpiry,
          card_cvv: cardCvv,
          merchant_id: 'MERCHANT-RESILIENCE-01',
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setLastPaymentResult(data);
      } else {
        const err = await res.json().catch(() => ({ detail: 'Échec de traitement' }));
        setPaymentError(err.detail || 'Erreur lors de la transaction.');
      }
    } catch {
      setPaymentError('Impossible de joindre le service de paiement (Service DOWN ou Bloqué)');
    } finally {
      setIsSubmitting(false);
      fetchData();
    }
  };

  // Simulation d'un lot de 10 paiements
  const handleSimulateBatch = async () => {
    setIsRefreshing(true);
    try {
      await fetch('/api/v1/payments/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count: 10, currency: 'EUR' }),
      });
      await fetchData();
    } catch (err) {
      console.error(err);
    } finally {
      setIsRefreshing(false);
    }
  };

  // Déclenchement d'un incident contrôlé (Chaos)
  const handleTriggerChaos = async () => {
    try {
      await fetch('/api/v1/chaos/configure', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ injected_latency_ms: 1500, injected_error_rate: 0.6 }),
      });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  // Réinitialisation de l'état nominal
  const handleResetChaos = async () => {
    try {
      await fetch('/api/v1/chaos/reset', { method: 'POST' });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-[#080C15] text-slate-100 p-4 md:p-8">
      {/* Header & Bandeau Statut */}
      <header className="max-w-7xl mx-auto mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <span className="p-2 bg-indigo-600/20 text-indigo-400 rounded-lg border border-indigo-500/30">
              <ShieldCheck className="w-6 h-6" />
            </span>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                PROJECT RESILIENCE-ALPHA
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded bg-indigo-900/60 text-indigo-300 border border-indigo-700/50">
                  K8s Cluster Ready
                </span>
              </h1>
              <p className="text-xs text-slate-400">Plateforme de paiement cyber-résiliente & Supervision Zero-Touch</p>
            </div>
          </div>
        </div>

        {/* Pilules de statut */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs">
            <span className="text-slate-400">Transactions :</span>
            <span className="font-semibold text-white">{totalTx}</span>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs">
            <span className="text-slate-400">Uptime :</span>
            <span className="font-semibold text-white">{Math.round(uptime)}s</span>
          </div>

          {healthStatus === 'HEALTHY' && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              SYSTÈME OPÉRATIONNEL
            </div>
          )}

          {healthStatus !== 'HEALTHY' && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-rose-400 animate-ping" />
              PERTURBATION DÉTECTÉE
            </div>
          )}

          {chaosState.is_active && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold">
              <AlertTriangle className="w-3.5 h-3.5" />
              CHAOS ACTIF (Latence {chaosState.injected_latency_ms}ms)
            </div>
          )}
        </div>
      </header>

      {/* Grille Principale */}
      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Colonne Gauche : Terminal de Paiement (7 colonnes) */}
        <section className="lg:col-span-7 space-y-6">
          <div className="bg-[#101726] border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                <CreditCard className="w-5 h-5 text-indigo-400" />
                Terminal de Paiement Sécurisé (Fictif)
              </h2>
              <span className="text-xs text-slate-400 flex items-center gap-1">
                <Lock className="w-3.5 h-3.5 text-emerald-400" /> Sandbox Bancaire
              </span>
            </div>

            {/* Carte Bancaire Virtuelle Stylée */}
            <div className="relative overflow-hidden w-full h-48 rounded-xl bg-gradient-to-tr from-indigo-900 via-indigo-700 to-slate-800 p-5 shadow-2xl mb-6 text-white border border-indigo-400/20">
              <div className="flex justify-between items-start mb-6">
                <div className="w-12 h-9 bg-amber-300/80 rounded-md border border-amber-200/50 shadow-inner flex items-center justify-center">
                  <div className="w-8 h-5 border border-amber-600/40 rounded-sm" />
                </div>
                <span className="text-lg font-extrabold tracking-widest text-indigo-200">RESILIENCE PAY</span>
              </div>
              <div className="text-lg md:text-xl font-mono tracking-widest mb-4">
                {cardNumber || '•••• •••• •••• ••••'}
              </div>
              <div className="flex justify-between items-end text-xs uppercase tracking-wider text-slate-200">
                <div>
                  <span className="block text-[10px] text-indigo-200">Titulaire</span>
                  <span className="font-semibold">{customerName || 'NOM DU CLIENT'}</span>
                </div>
                <div>
                  <span className="block text-[10px] text-indigo-200">Expire</span>
                  <span className="font-semibold">{cardExpiry || 'MM/AA'}</span>
                </div>
              </div>
            </div>

            {/* Formulaire de paiement */}
            <form onSubmit={handlePayment} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Montant à régler (€)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="1"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    required
                    className="w-full bg-slate-900/90 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Devise</label>
                  <select
                    value={currency}
                    onChange={(e) => setCurrency(e.target.value)}
                    className="w-full bg-slate-900/90 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="EUR">EUR (€)</option>
                    <option value="USD">USD ($)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Nom complet du porteur</label>
                <input
                  type="text"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  required
                  className="w-full bg-slate-900/90 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="col-span-2">
                  <label className="block text-xs font-medium text-slate-400 mb-1">Numéro de Carte (Fictif)</label>
                  <input
                    type="text"
                    value={cardNumber}
                    onChange={(e) => setCardNumber(e.target.value)}
                    required
                    className="w-full bg-slate-900/90 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">CVV</label>
                  <input
                    type="text"
                    maxLength={4}
                    value={cardCvv}
                    onChange={(e) => setCardCvv(e.target.value)}
                    className="w-full bg-slate-900/90 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              {/* Bouton d'action de paiement */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full mt-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold py-3 px-4 rounded-xl shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center gap-2"
              >
                {isSubmitting ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Traitement de l'autorisation...
                  </>
                ) : (
                  <>
                    <span>Effectuer le paiement de {amount} {currency}</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

            {/* Notification de Résultat Succès */}
            {lastPaymentResult && (
              <div className="mt-5 p-4 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-emerald-200 flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 mt-0.5 shrink-0" />
                <div className="text-xs space-y-1">
                  <div className="font-bold text-sm text-emerald-300">Transaction Autorisée avec Succès !</div>
                  <div>Réf : <span className="font-mono text-white">{lastPaymentResult.reference}</span></div>
                  <div>ID : <span className="font-mono text-slate-300">{lastPaymentResult.transaction_id}</span></div>
                  <div>Code Auth : <span className="font-mono text-emerald-300 font-semibold">{lastPaymentResult.auth_code}</span></div>
                </div>
              </div>
            )}

            {/* Notification d'Échec */}
            {paymentError && (
              <div className="mt-5 p-4 rounded-xl bg-rose-950/60 border border-rose-500/40 text-rose-200 flex items-start gap-3">
                <XCircle className="w-5 h-5 text-rose-400 mt-0.5 shrink-0" />
                <div className="text-xs space-y-1">
                  <div className="font-bold text-sm text-rose-300">Échec de la transaction</div>
                  <div>{paymentError}</div>
                  <div className="text-slate-400">Le système est actuellement instable ou en cours de remédiation autonome.</div>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Colonne Droite : Supervision & Actions Démo (5 colonnes) */}
        <section className="lg:col-span-5 space-y-6">
          {/* Panneau d'Actions Rapides & Chaos (Idéal pour la Démo) */}
          <div className="bg-[#101726] border border-slate-800 rounded-2xl p-6 shadow-xl">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
              <Zap className="w-5 h-5 text-amber-400" />
              Commandes de Démonstration Live
            </h2>

            <div className="space-y-3">
              <button
                onClick={handleSimulateBatch}
                disabled={isRefreshing}
                className="w-full text-left px-4 py-3 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 transition flex items-center justify-between"
              >
                <div>
                  <div className="text-xs font-semibold text-white">⚡ Générer 10 transactions de trafic</div>
                  <div className="text-[11px] text-slate-400">Alimente les métriques Prometheus et le modèle ML</div>
                </div>
                <RefreshCw className={`w-4 h-4 text-slate-400 ${isRefreshing ? 'animate-spin' : ''}`} />
              </button>

              <button
                onClick={handleTriggerChaos}
                className="w-full text-left px-4 py-3 rounded-xl bg-rose-950/40 hover:bg-rose-900/40 border border-rose-700/50 transition flex items-center justify-between"
              >
                <div>
                  <div className="text-xs font-semibold text-rose-300">💥 Simuler Attaque (Latence + Erreurs 500)</div>
                  <div className="text-[11px] text-rose-400/80">Provoque l'anomalie détectée par le modèle ML</div>
                </div>
                <AlertTriangle className="w-4 h-4 text-rose-400" />
              </button>

              <button
                onClick={handleResetChaos}
                className="w-full text-left px-4 py-3 rounded-xl bg-emerald-950/40 hover:bg-emerald-900/40 border border-emerald-700/50 transition flex items-center justify-between"
              >
                <div>
                  <div className="text-xs font-semibold text-emerald-300">🔄 Réinitialiser à l'état nominal</div>
                  <div className="text-[11px] text-emerald-400/80">Rétablit les paramètres sans latence ni erreur</div>
                </div>
                <RefreshCw className="w-4 h-4 text-emerald-400" />
              </button>
            </div>
          </div>

          {/* Flux des Dernières Transactions en direct */}
          <div className="bg-[#101726] border border-slate-800 rounded-2xl p-6 shadow-xl">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
              <Activity className="w-5 h-5 text-indigo-400" />
              Dernières Transactions (Temps Réel)
            </h2>

            {transactions.length === 0 ? (
              <p className="text-xs text-slate-500 py-4 text-center">Aucune transaction enregistrée pour l'instant.</p>
            ) : (
              <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
                {transactions.map((tx) => (
                  <div
                    key={tx.transaction_id}
                    className="p-2.5 rounded-lg bg-slate-900/70 border border-slate-800 flex items-center justify-between text-xs"
                  >
                    <div>
                      <div className="font-semibold text-slate-200">{tx.customer_name}</div>
                      <div className="text-[10px] text-slate-500 font-mono">Carte **** {tx.card_last4}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-white">{tx.amount.toFixed(2)} {tx.currency}</div>
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                        {tx.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
