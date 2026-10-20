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
  ArrowRight,
  Terminal,
  Trash2,
  Play,
  Layers,
  Sparkles,
  ShoppingBag,
  ExternalLink
} from 'lucide-react';

export default function App() {
  // Détection du chemin d'accès (route native sans bibliothèque externe)
  // "/" ou tout chemin standard -> Terminal de paiement client épuré
  // "/supervision" -> Centre de supervision SOC & Audit Zero-Touch
  const [currentPath, setCurrentPath] = useState(
    typeof window !== 'undefined' ? window.location.pathname : '/'
  );

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
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isRemediating, setIsRemediating] = useState(false);

  // Logs et historique de remédiation
  const [remediationLogs, setRemediationLogs] = useState([]);
  const [remediationHistory, setRemediationHistory] = useState([]);

  // Gestion intelligente des inputs de carte bancaire (chiffres uniquement + espaces auto)
  const handleCardNumberChange = (e) => {
    // Extrait uniquement les chiffres, max 16
    const raw = e.target.value.replace(/\D/g, '').slice(0, 16);
    // Insère un espace tous les 4 chiffres
    const formatted = raw.match(/.{1,4}/g)?.join(' ') || '';
    setCardNumber(formatted);
  };

  const handleExpiryChange = (e) => {
    // Extrait uniquement les chiffres, max 4
    const raw = e.target.value.replace(/\D/g, '').slice(0, 4);
    if (raw.length >= 3) {
      setCardExpiry(`${raw.slice(0, 2)}/${raw.slice(2)}`);
    } else {
      setCardExpiry(raw);
    }
  };

  const handleCvvChange = (e) => {
    // Extrait uniquement les chiffres, max 3 ou 4
    const raw = e.target.value.replace(/\D/g, '').slice(0, 4);
    setCardCvv(raw);
  };

  const handleNameChange = (e) => {
    // Met le nom en majuscules pour le rendu carte
    setCustomerName(e.target.value.toUpperCase());
  };

  // Détection automatique du type de carte
  const getCardBrand = (number) => {
    const clean = number.replace(/\s+/g, '');
    if (clean.startsWith('4')) return { name: 'VISA', color: 'from-blue-900 via-indigo-900 to-slate-900' };
    if (/^(5[1-5]|2[2-7])/.test(clean)) return { name: 'MASTERCARD', color: 'from-orange-950 via-red-950 to-slate-900' };
    if (/^3[47]/.test(clean)) return { name: 'AMEX', color: 'from-cyan-950 via-teal-950 to-slate-900' };
    return { name: 'CB', color: 'from-indigo-950 via-slate-900 to-slate-950' };
  };

  const cardBrand = getCardBrand(cardNumber);

  // Polling des données de santé, transactions et logs
  const fetchData = async () => {
    try {
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
      const txRes = await fetch('/api/v1/payments?limit=8');
      if (txRes.ok) {
        const data = await txRes.json();
        setTransactions(data.transactions || []);
      }
    } catch (e) {
      console.warn("Erreur transactions", e);
    }

    try {
      const chaosRes = await fetch('/api/v1/chaos/status');
      if (chaosRes.ok) {
        const cData = await chaosRes.json();
        setChaosState(cData);
      }
    } catch (e) {
      console.warn("Erreur chaos", e);
    }

    try {
      const logsRes = await fetch('/remediation/api/v1/remediation/logs');
      if (logsRes.ok) {
        const lData = await logsRes.json();
        setRemediationLogs(lData.logs || []);
      }
    } catch (e) {
      console.warn("Erreur logs", e);
    }

    try {
      const histRes = await fetch('/remediation/api/v1/remediation/history');
      if (histRes.ok) {
        const hData = await histRes.json();
        setRemediationHistory(hData.history || []);
      }
    } catch (e) {
      console.warn("Erreur historique", e);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  // Soumission d'une transaction fictive
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

  // Actions de démo
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

  const handleResetChaos = async () => {
    try {
      await fetch('/api/v1/chaos/reset', { method: 'POST' });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleTriggerRemediation = async () => {
    setIsRemediating(true);
    try {
      await fetch('/remediation/api/v1/remediation/trigger', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: "Déclenchement live via Dashboard Démo" }),
      });
      await fetch('/api/v1/chaos/reset', { method: 'POST' });
      await fetchData();
    } catch (err) {
      console.error(err);
    } finally {
      setIsRemediating(false);
    }
  };

  const handleClearLogs = async () => {
    try {
      await fetch('/remediation/api/v1/remediation/logs', { method: 'DELETE' });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-[#070A12] text-slate-100 flex flex-col font-sans">
      {/* Barre de navigation uniquement visible en mode /supervision */}
      {isSupervision ? (
        <header className="border-b border-slate-800 bg-[#0B0F1A]/90 backdrop-blur-md sticky top-0 z-50 px-4 md:px-8 py-3.5">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-3">
            {/* Logo & Identité SOC */}
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-tr from-indigo-600 to-indigo-400 text-white rounded-xl shadow-lg shadow-indigo-600/30">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <span className="font-extrabold tracking-wider text-base text-white flex items-center gap-2">
                  RESILIENCE SOC
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-700/60 uppercase">
                    Supervision & Audit
                  </span>
                </span>
                <p className="text-[11px] text-slate-400">Centre d'Opérations de Sécurité & Zero-Touch Recovery</p>
              </div>
            </div>

            {/* Pastille de Santé Rapide */}
            <div className="flex items-center gap-2 text-xs font-mono">
              {healthStatus === 'HEALTHY' ? (
                <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/30 text-emerald-400">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  CLUSTER ONLINE (200 OK)
                </span>
              ) : (
                <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-950/80 border border-rose-500/30 text-rose-400">
                  <span className="w-2 h-2 rounded-full bg-rose-400 animate-ping" />
                  INCIDENT EN COURS
                </span>
              )}
            </div>
          </div>
        </header>
      ) : (
        /* En-tête épuré et sobre pour la page client du terminal de paiement */
        <header className="border-b border-slate-800/60 bg-[#0B0F1A]/50 backdrop-blur-sm px-4 md:px-8 py-4">
          <div className="max-w-5xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 bg-indigo-600/30 text-indigo-400 border border-indigo-500/40 rounded-lg">
                <Lock className="w-4 h-4" />
              </div>
              <span className="font-bold tracking-wide text-sm text-slate-200">
                PAIEMENT SÉCURISÉ
              </span>
            </div>
            <span className="text-[11px] text-slate-400 font-mono flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Chiffrement TLS 1.3
            </span>
          </div>
        </header>
      )}

      {/* ========================================================================= */}
      {/* VUE 1 : PAGE CARTE DE PAIEMENT CLIENT ÉPURÉE (ACCESSIBLE SUR "/")         */}
      {/* ========================================================================= */}
      {!isSupervision && (
        <main className="flex-1 max-w-5xl mx-auto w-full p-4 md:p-8 flex flex-col justify-center">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            {/* Colonne Gauche : Récapitulatif Commande & Rendu Carte Virtuelle (5 cols) */}
            <div className="lg:col-span-5 space-y-6">
              {/* Carte Bancaire Virtuelle Réaliste */}
              <div className={`relative overflow-hidden w-full h-56 rounded-2xl bg-gradient-to-tr ${cardBrand.color} p-6 shadow-2xl text-white border border-white/10 transition-all duration-500 transform hover:scale-[1.02]`}>
                {/* Reflet Holographique */}
                <div className="absolute -top-16 -right-16 w-48 h-48 bg-white/5 rounded-full blur-xl pointer-events-none" />

                <div className="flex justify-between items-start mb-6">
                  {/* Puce Électronique Réaliste */}
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

                {/* Numéro avec espaces tous les 4 chiffres */}
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

              {/* Récapitulatif du panier fictif */}
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
                  <span className="font-bold text-white font-mono">{amount} {currency}</span>
                </div>
                <div className="text-[11px] text-slate-400 pt-2 flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>Environnement bac à sable — Aucune donnée bancaire réelle requise.</span>
                </div>
              </div>
            </div>

            {/* Colonne Droite : Formulaire avec Inputs Intelligents (7 cols) */}
            <div className="lg:col-span-7 bg-[#0F1626] border border-slate-800 rounded-2xl p-6 md:p-8 shadow-xl">
              <div className="mb-6">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <span>Informations de Paiement</span>
                </h2>
                <p className="text-xs text-slate-400 mt-1">Saisissez les coordonnées de votre carte de test ci-dessous.</p>
              </div>

              <form onSubmit={handlePayment} className="space-y-4">
                {/* Montant et Devise */}
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

                {/* Nom du titulaire */}
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

                {/* Numéro de carte avec espaces automatiques et chiffres uniquement */}
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
                  <p className="text-[10px] text-slate-500 mt-1">Espaces insérés automatiquement. Uniquement des chiffres acceptés.</p>
                </div>

                {/* Date d'expiration et CVV */}
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

                {/* Bouton de confirmation de paiement */}
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

              {/* Récépissé en cas de SUCCÈS */}
              {lastPaymentResult && (
                <div className="mt-6 p-4 rounded-xl bg-emerald-950/70 border border-emerald-500/50 text-emerald-200 animate-fadeIn">
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
                        Code d'Autorisation : <span className="font-mono text-emerald-300 font-bold">{lastPaymentResult.auth_code}</span>
                      </div>
                      <div className="text-[11px] text-slate-400 pt-1">
                        Transaction ID : <span className="font-mono">{lastPaymentResult.transaction_id}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Message d'Erreur lors d'une Panne ou Attaque */}
              {paymentError && (
                <div className="mt-6 p-4 rounded-xl bg-rose-950/70 border border-rose-500/50 text-rose-200 animate-fadeIn">
                  <div className="flex items-start gap-3">
                    <XCircle className="w-6 h-6 text-rose-400 shrink-0 mt-0.5" />
                    <div className="text-xs space-y-1">
                      <div className="font-bold text-sm text-rose-300">Échec de la Transaction</div>
                      <div>{paymentError}</div>
                      <p className="text-slate-400 text-[11px] pt-1">
                        Le système de paiement bancaire rencontre une perturbation passagère. Veuillez patienter ou renouveler votre tentative dans quelques instants.
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
        <main className="flex-1 max-w-7xl mx-auto w-full p-4 md:p-8 space-y-8">
          {/* Bandeau de Chiffres Clés */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-[#0F1626] border border-slate-800 rounded-xl p-4">
              <span className="text-xs text-slate-400 block mb-1">Disponibilité Système</span>
              <span className={`text-lg font-bold font-mono ${healthStatus === 'HEALTHY' ? 'text-emerald-400' : 'text-rose-400'}`}>
                {healthStatus}
              </span>
            </div>
            <div className="bg-[#0F1626] border border-slate-800 rounded-xl p-4">
              <span className="text-xs text-slate-400 block mb-1">Temps de Fonctionnement</span>
              <span className="text-lg font-bold font-mono text-white">{Math.round(uptime)}s</span>
            </div>
            <div className="bg-[#0F1626] border border-slate-800 rounded-xl p-4">
              <span className="text-xs text-slate-400 block mb-1">Transactions Enregistrées</span>
              <span className="text-lg font-bold font-mono text-indigo-400">{totalTx}</span>
            </div>
            <div className="bg-[#0F1626] border border-slate-800 rounded-xl p-4">
              <span className="text-xs text-slate-400 block mb-1">Événements de Remédiation</span>
              <span className="text-lg font-bold font-mono text-amber-400">{remediationHistory.length}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Colonne Gauche : Panneau de Contrôle & Démo Live (5 cols) */}
            <div className="lg:col-span-5 space-y-6">
              <div className="bg-[#0F1626] border border-slate-800 rounded-2xl p-6 shadow-xl">
                <h2 className="text-base font-bold text-white flex items-center gap-2 mb-4">
                  <Zap className="w-5 h-5 text-amber-400" />
                  Commandes de Démonstration Live
                </h2>

                <div className="space-y-3">
                  <button
                    onClick={handleSimulateBatch}
                    disabled={isRefreshing}
                    className="w-full text-left px-4 py-3 rounded-xl bg-slate-900/80 hover:bg-slate-800/80 border border-slate-700/80 transition flex items-center justify-between"
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
                    onClick={handleTriggerRemediation}
                    disabled={isRemediating}
                    className="w-full text-left px-4 py-3 rounded-xl bg-indigo-950/40 hover:bg-indigo-900/40 border border-indigo-700/50 transition flex items-center justify-between"
                  >
                    <div>
                      <div className="text-xs font-semibold text-indigo-300">🛡️ Déclencher Remédiation Autonome</div>
                      <div className="text-[11px] text-indigo-400/80">Rollout restart K8s + Preuve par transaction test</div>
                    </div>
                    <Play className={`w-4 h-4 text-indigo-400 ${isRemediating ? 'animate-spin' : ''}`} />
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

              {/* Flux des Dernières Transactions */}
              <div className="bg-[#0F1626] border border-slate-800 rounded-2xl p-6 shadow-xl">
                <h2 className="text-base font-bold text-white flex items-center gap-2 mb-4">
                  <Activity className="w-5 h-5 text-indigo-400" />
                  Dernières Transactions (Temps Réel)
                </h2>

                {transactions.length === 0 ? (
                  <p className="text-xs text-slate-500 py-4 text-center">Aucune transaction enregistrée.</p>
                ) : (
                  <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
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
            </div>

            {/* Colonne Droite : Console de Logs et d'Audit de Remédiation (7 cols) */}
            <div className="lg:col-span-7 bg-[#0F1626] border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <Terminal className="w-5 h-5 text-emerald-400" />
                  <h3 className="text-base font-bold text-white uppercase tracking-wide">
                    Console de Remédiation & Audit Zero-Touch
                  </h3>
                </div>
                <button
                  onClick={handleClearLogs}
                  title="Vider les logs"
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              {/* Écran Terminal Noir avec Défilement */}
              <div className="bg-[#050811] rounded-xl border border-slate-800 p-4 font-mono text-xs max-h-96 overflow-y-auto space-y-2 shadow-inner">
                {remediationLogs.length === 0 ? (
                  <div className="text-slate-500 text-center py-8">
                    En attente d'événements... Les sondes Kubernetes et le récepteur ML sont opérationnels.
                  </div>
                ) : (
                  remediationLogs.map((log, index) => {
                    let badgeClass = "bg-slate-800 text-slate-300";
                    if (log.level === "ALERT") badgeClass = "bg-rose-950 text-rose-300 border border-rose-800";
                    if (log.level === "ACTION") badgeClass = "bg-indigo-950 text-indigo-300 border border-indigo-800";
                    if (log.level === "VERIFY") badgeClass = "bg-amber-950 text-amber-300 border border-amber-800";
                    if (log.level === "SUCCESS") badgeClass = "bg-emerald-950 text-emerald-300 border border-emerald-700 font-bold";
                    if (log.level === "ERROR") badgeClass = "bg-red-900 text-white font-bold";

                    return (
                      <div key={index} className="flex items-start gap-2.5 leading-relaxed hover:bg-slate-900/60 p-1.5 rounded">
                        <span className="text-slate-500 select-none text-[11px]">[{log.time}]</span>
                        <span className={`px-1.5 py-0.5 rounded text-[10px] uppercase font-semibold shrink-0 ${badgeClass}`}>
                          {log.level}
                        </span>
                        <span className={`text-[12px] break-all ${log.level === "SUCCESS" ? "text-emerald-300 font-semibold" : log.level === "ALERT" ? "text-rose-300" : "text-slate-300"}`}>
                          {log.message}
                        </span>
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
