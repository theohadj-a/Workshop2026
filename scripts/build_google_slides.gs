/**
 * =========================================================================
 * GOOGLE SLIDES AUTO-GENERATOR COMPLET — PROJECT RESILIENCE-ALPHA
 * Workshop National Bac+5 EPSI 2026 (15 Diapositives Intégrales)
 * =========================================================================
 * 
 * MODE D'EMPLOI EN 3 ÉTAPES :
 * 1. Ouvrez une nouvelle présentation Google Slides (tapez "slides.new" dans Chrome).
 * 2. Cliquez dans le menu sur : Extensions > Apps Script.
 * 3. Remplacez le code par ce script complet et cliquez sur le bouton "Exécuter" (Run).
 * 
 * En 10 secondes, les 15 diapositives sont créées avec la charte graphique EPSI,
 * les cartes d'architecture, les matrices d'attaques et toutes les notes du présentateur !
 */

function generateResilienceAlphaSlides() {
  var pres = SlidesApp.getActivePresentation();
  
  // Charte graphique EPSI officielle (Page 9 du sujet)
  var COLOR_BG = '#E4E6F3';         // Fond doux diapo
  var COLOR_NAVY = '#261E48';       // Texte principal / Titres
  var COLOR_ACCENT = '#A1A6D4';     // Cartes & Bordures
  var COLOR_CARD = '#FFFFFF';       // Cartes blanches lisibles
  var COLOR_DARK_CARD = '#261E48';  // Cartes sombres contrastées
  var COLOR_CARD_SOFT = '#F1F2FA';  // Cartes neutres
  var COLOR_RED = '#DC2626';        // Rouge alerte Red Team
  var COLOR_GREEN = '#16A34A';      // Vert succès transaction
  var COLOR_BLUE = '#2563EB';       // Bleu AIOps
  var COLOR_AMBER = '#D97706';      // Orange dégradation
  var COLOR_WHITE = '#FFFFFF';

  function addHeader(slide, title, category) {
    category = category || "WORKSHOP M2 EPSI • PROJECT RESILIENCE-ALPHA";
    var catBox = slide.insertTextBox(category.toUpperCase(), 40, 18, 640, 18);
    catBox.getText().getTextStyle()
      .setFontFamily("Montserrat")
      .setFontSize(8.5)
      .setBold(true)
      .setForegroundColor(COLOR_ACCENT);

    var titleBox = slide.insertTextBox(title, 40, 36, 640, 36);
    titleBox.getText().getTextStyle()
      .setFontFamily("Montserrat")
      .setFontSize(17)
      .setBold(true)
      .setForegroundColor(COLOR_NAVY);
  }

  function addCard(slide, left, top, width, height, bgColor, borderColor) {
    bgColor = bgColor || COLOR_CARD;
    borderColor = borderColor || COLOR_ACCENT;
    var shape = slide.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE, left, top, width, height);
    shape.getFill().setSolidFill(bgColor);
    shape.getBorder().setSolidFill(borderColor).setWeight(1.5);
    return shape;
  }

  function setNotes(slide, text) {
    slide.getNotesPage().getSpeakerNotesShape().getText().setText(text);
  }

  // -------------------------------------------------------------------------
  // SLIDE 1 : TITRE & CONSORTIUM
  // -------------------------------------------------------------------------
  var s1 = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  s1.getBackground().setSolidFill(COLOR_NAVY);
  addCard(s1, 30, 30, 660, 340, COLOR_NAVY, COLOR_ACCENT);
  
  var b1 = s1.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE, 50, 45, 300, 24);
  b1.getFill().setSolidFill(COLOR_ACCENT);
  b1.getBorder().setTransparent();
  b1.getText().setText("DIRECTION NATIONALE DE LA SÛRETÉ NUMÉRIQUE");
  b1.getText().getTextStyle().setFontFamily("Montserrat").setFontSize(8).setBold(true).setForegroundColor(COLOR_NAVY);

  var tb1 = s1.insertTextBox("PROJECT RESILIENCE-ALPHA\nCyber-Résilience Autonome & Reprise sans Intervention Humaine (Zero-Touch)\n« Tout système finit par tomber. La vraie question : le vôtre saura-t-il se relever seul ? »", 50, 75, 620, 120);
  tb1.getText().getTextStyle().setFontFamily("Montserrat");
  tb1.getText().getParagraphs()[0].getTextStyle().setFontSize(26).setBold(true).setForegroundColor(COLOR_WHITE);
  tb1.getText().getParagraphs()[1].getTextStyle().setFontSize(12).setItalic(true).setForegroundColor(COLOR_BG);
  tb1.getText().getParagraphs()[2].getTextStyle().setFontSize(10).setForegroundColor(COLOR_ACCENT);

  var members = [
    { n: "Théo", r: "Architecture K8s" },
    { n: "Mael", r: "Microservices Dev" },
    { n: "Flora", r: "Cybersécurité WAF" },
    { n: "Fely", r: "AIOps & ML" },
    { n: "Aymeric", r: "Gouvernance EBIOS" }
  ];
  for (var i = 0; i < members.length; i++) {
    var mx = 50 + i * 125;
    var mc = s1.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE, mx, 250, 115, 90);
    mc.getFill().setSolidFill('#302858');
    mc.getBorder().setSolidFill(COLOR_ACCENT);
    mc.getText().setText(members[i].n + "\n" + members[i].r);
    mc.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(13).setBold(true).setForegroundColor(COLOR_WHITE);
    mc.getText().getParagraphs()[1].getTextStyle().setFontFamily("Montserrat").setFontSize(9).setForegroundColor(COLOR_BG);
  }
  setNotes(s1, "[PITCH D'OUVERTURE - 0:00 à 0:45]\nBonjour à tous, membres du jury. À l'automne 2026, la question n'est plus de savoir si un système d'information critique va subir une cyberattaque, mais à quelle vitesse et avec quel degré d'autonomie il est capable de s'en relever. Notre consortium — Théo, Mael, Flora, Fely et Aymeric — a conçu et implémenté PROJECT RESILIENCE-ALPHA : cyber-résilience autonome Zero-Touch validée par une nouvelle transaction bancaire.");

  // -------------------------------------------------------------------------
  // SLIDE 2 : CONTEXTE & DÉFI MÉTIER
  // -------------------------------------------------------------------------
  var s2 = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  s2.getBackground().setSolidFill(COLOR_BG);
  addHeader(s2, "Le Défi National : Continuité Métier & Zero-Touch Recovery");

  var s2c1 = addCard(s2, 40, 85, 205, 290, COLOR_CARD);
  s2c1.getText().setText("1. Contexte Bancaire Critique\n\n• Plateforme transactionnelle soumise à des pannes récurrentes.\n• Interventions manuelles lentes, complexes et non reproductibles.\n• Pertes financières immédiates et rupture de confiance.\n• Obligations de conformité accrues (DORA & NIS2).");
  s2c1.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(13).setBold(true).setForegroundColor(COLOR_NAVY);

  var s2c2 = addCard(s2, 255, 85, 205, 290, COLOR_CARD);
  s2c2.getText().setText("2. Le Défi DNSN\n\n• SI conteneurisé complet (Front React, API REST, Auth, PostgreSQL).\n• Attaque réelle menée depuis un PC Attaquant physiquement séparé.\n• Détection Machine Learning (Isolation Forest) et non simples seuils.\n• Auto-guérison sans aucune intervention humaine (Zero-Touch).");
  s2c2.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(13).setBold(true).setForegroundColor(COLOR_NAVY);

  var s2c3 = addCard(s2, 470, 85, 210, 290, COLOR_DARK_CARD, COLOR_RED);
  s2c3.getText().setText("3. Règle d'Or & Preuve\n\nZÉRO INTERVENTION :\nToute action manuelle pendant la démo entraîne immédiatement 0/5 sur l'axe remédiation.\n\nPREUVE PAR LA TRANSACTION :\nLe redémarrage du pod ne suffit pas : le système doit réussir un paiement réel après reprise.\n\nVISIBILITÉ CONTINUE :\nÉtat visible avant, pendant et après l'incident.");
  s2c3.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(13).setBold(true).setForegroundColor(COLOR_WHITE);

  setNotes(s2, "[CADRAGE STRATÉGIQUE - 0:45 à 1:15]\nLe cahier des charges posé par la Direction Nationale de la Sûreté Numérique est sans ambiguïté : l'indisponibilité se chiffre en milliers d'euros par minute. Relancer un service à la main est anachronique. Attention : toute intervention humaine vaut 0 éliminatoire. Notre système s'auto-guérit et le prouve par une transaction.");

  // -------------------------------------------------------------------------
  // SLIDE 3 : ARCHITECTURE GLOBALE — 5 PILIERS
  // -------------------------------------------------------------------------
  var s3 = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  s3.getBackground().setSolidFill(COLOR_BG);
  addHeader(s3, "Architecture Globale : L'Interconnexion des 5 Piliers");

  var pData = [
    { t: "DEV", s: "Microservices", c: "• FastAPI Payment API\n• Auth JWT Bearer\n• Front React/Tailwind\n• Remediation Engine", b: COLOR_NAVY },
    { t: "INFRA", s: "Kubernetes & Obs", c: "• Helm Chart officiel\n• 3 réplicas + HPA\n• Prometheus (1s)\n• Grafana & Loki", b: COLOR_NAVY },
    { t: "CYBER", s: "Défense Profondeur", c: "• WAF Nginx L7\n• Anti-Scanner (403)\n• Rate Limit 5r/s (429)\n• Console Red Team", b: COLOR_RED },
    { t: "IA / DATA", s: "AIOps ML", c: "• Isolation Forest\n• Vecteur 4D temps réel\n• Inférence < 5ms\n• Webhook alerte", b: COLOR_BLUE },
    { t: "GOUV.", s: "Risques & DORA", c: "• EBIOS RM (5 ateliers)\n• DORA Art. 6, 17, 24\n• Directive NIS2\n• RTO < 20s | RPO = 0", b: COLOR_NAVY }
  ];
  for (var i = 0; i < pData.length; i++) {
    var px = 40 + i * 130;
    var pCard = addCard(s3, px, 85, 120, 235, COLOR_CARD, pData[i].b);
    pCard.getText().setText(pData[i].t + "\n" + pData[i].s + "\n\n" + pData[i].c);
    pCard.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(12).setBold(true).setForegroundColor(pData[i].b);
    pCard.getText().getParagraphs()[1].getTextStyle().setFontFamily("Montserrat").setFontSize(8).setForegroundColor(COLOR_NAVY);
  }

  var flowCard = addCard(s3, 40, 330, 640, 45, COLOR_DARK_CARD, COLOR_ACCENT);
  flowCard.getText().setText("CHAÎNE CONTINUE : PC Attaquant ➔ WAF Nginx ➔ API Paiement & K8s ➔ Métriques Prometheus ➔ Détecteur ML AIOps ➔ Webhook Remédiation ➔ Validation Transactionnelle.");
  flowCard.getText().getTextStyle().setFontFamily("Montserrat").setFontSize(9).setForegroundColor(COLOR_WHITE);

  setNotes(s3, "[ARCHITECTURE & 5 PILIERS - 1:15 à 1:45]\nNos 5 piliers ne sont pas des silos : ils constituent une boucle continue d'interconnexion. La télémétrie de l'INFRA et du DEV alimente l'IA. L'alerte IA actionne la remédiation. La CYBER éprouve l'ensemble et la GOUVERNANCE garantit la conformité DORA/NIS2.");

  // -------------------------------------------------------------------------
  // SLIDE 4 : PILIER DEV — CŒUR MÉTIER & REMÉDIATION
  // -------------------------------------------------------------------------
  var s4 = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  s4.getBackground().setSolidFill(COLOR_BG);
  addHeader(s4, "Pilier DEV : Architecture Microservices & Supervision SOC");

  var s4c1 = addCard(s4, 40, 85, 315, 290, COLOR_CARD);
  s4c1.getText().setText("Microservices Conteneurisés Métier\n\n• payment-api (FastAPI) :\nAPI transactionnelle asynchrone, écriture PostgreSQL, endpoints /health et /metrics Prometheus.\n\n• auth-service (Microservice JWT) :\nAuthentification forte RBAC (Admin SOC vs Opérateur). Cloisonnement strict des commandes de remédiation par token Bearer.\n\n• dashboard-ui (React + Tailwind) :\nInterface web unifiée : terminal client public pour simuler les achats, et console de supervision SOC temps réel.");
  s4c1.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(13).setBold(true).setForegroundColor(COLOR_NAVY);

  var s4c2 = addCard(s4, 365, 85, 315, 290, COLOR_CARD_SOFT);
  s4c2.getText().setText("Le Moteur de Remédiation & Preuve Métier\n\n➔ Surveillance Native K8s (Niveau 1) :\nSondes Liveness/Readiness. En cas de crash physique (OOMKilled), K8s relance immédiatement le conteneur.\n\n➔ Réaction Intelligente ML (Niveau 2) :\nEn cas d'asphyxie sans crash (Slowloris, Chaos), le moteur ordonne un rollout restart progressif sans coupure.\n\n➔ La Preuve par la Transaction :\nDès notification de retour au vert, verifier.py injecte un paiement réel (POST /payments) et vérifie le HTTP 201 Created.");
  s4c2.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(13).setBold(true).setForegroundColor(COLOR_NAVY);

  setNotes(s4, "[DÉVELOPPEMENT - 1:45 à 2:15]\nCôté développement : microservices FastAPI légers et performants. Deux points clés : le cloisonnement des privilèges par jetons JWT Bearer chiffrés, et le module verifier.py qui transmet une transaction réelle après la reprise pour valider le retour au vert.");

  // -------------------------------------------------------------------------
  // SLIDE 5 : PILIER INFRA — K8S, HELM & OBSERVABILITÉ
  // -------------------------------------------------------------------------
  var s5 = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  s5.getBackground().setSolidFill(COLOR_BG);
  addHeader(s5, "Pilier INFRA : Déploiement Helm, Haute Disponibilité & Métriques");

  var s5c1 = addCard(s5, 40, 85, 205, 290, COLOR_CARD);
  s5c1.getText().setText("Orchestration K8s / Helm\n\n• Helm Chart officiel 'resilience-alpha' entièrement paramétrable (values.yaml).\n• 3 réplicas par défaut pour l'API de paiement (haute disponibilité).\n• Kind Cluster avec Ingress Nginx (ports 80/443 de l'hôte).\n• Scripts de build automatisés cross-plateformes (Linux, WSL2, macOS).");
  s5c1.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(12).setBold(true).setForegroundColor(COLOR_NAVY);

  var s5c2 = addCard(s5, 255, 85, 205, 290, COLOR_CARD);
  s5c2.getText().setText("Élasticité & Sécurité Réseau\n\n• Horizontal Pod Autoscaler (HPA) : passage de 3 à 8 réplicas en cas de pic CPU (>70%).\n• NetworkPolicies Kubernetes : isolation stricte entre pods.\n• PostgreSQL accessible uniquement depuis l'API de paiement.\n• Playbooks Ansible pour le déploiement reproductible.");
  s5c2.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(12).setBold(true).setForegroundColor(COLOR_NAVY);

  var s5c3 = addCard(s5, 470, 85, 210, 290, COLOR_CARD);
  s5c3.getText().setText("Chaîne d'Observabilité\n\n• Prometheus : scraping haute fréquence (intervalle 1s) sur /metrics.\n• Métriques clés : payment_http_requests_total, latence, requêtes actives.\n• Grafana : tableaux de bord visuels pour suivre le trafic nominal et les attaques.\n• Loki : centralisation des journaux Nginx et API sans surconsommation.");
  s5c3.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(12).setBold(true).setForegroundColor(COLOR_NAVY);

  setNotes(s5, "[INFRASTRUCTURE - 2:15 à 2:45]\nCôté infrastructure : Helm Chart officiel, 3 réplicas API et HPA élastique jusqu'à 8 pods. La chaîne d'observabilité Prometheus scrape les métriques à 1 seconde d'intervalle pour nourrir en temps réel notre modèle ML.");

  // -------------------------------------------------------------------------
  // SLIDE 6 : PILIER CYBER — WAF L7 & RED TEAM
  // -------------------------------------------------------------------------
  var s6 = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  s6.getBackground().setSolidFill(COLOR_BG);
  addHeader(s6, "Pilier CYBER : Défense en Profondeur WAF & Console Red Team");

  var s6c1 = addCard(s6, 40, 85, 315, 290, COLOR_CARD);
  s6c1.getText().setText("Filtrage Applicatif WAF L7 (Nginx)\n\n• 1. Blocage Scanners OWASP (HTTP 403) :\nUser-Agents malveillants réputés (sqlmap, nikto, nmap, dirbuster) immédiatement rejetés.\n\n• 2. Rate Limiting Sélectif (HTTP 429) :\nPlafond strict de 5 req/s (burst 10) sur /api/v1/payments.\n\n• 3. Durcissement HTTP (Standards ANSSI) :\nX-Frame-Options DENY, X-Content-Type-Options nosniff, CSP.\n\n• 4. Correction Brèche WAF Bypass :\nPorts internes restreints à 127.0.0.1. Obligation de transiter par le WAF.");
  s6c1.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(13).setBold(true).setForegroundColor(COLOR_NAVY);

  var s6c2 = addCard(s6, 365, 85, 315, 290, COLOR_CARD_SOFT, COLOR_RED);
  s6c2.getText().setText("Console Attaquant & Red Team Découplée\n\n• Découplage Physique Strict :\nModule exécuté depuis un ordinateur distinct, connecté via le point d'accès Wi-Fi RESILIENCE-G<n>.\n\n• Double Interface Red Team :\nDashboard Next.js (port 3001) et script CLI Python pour exécution automatisée.\n\n• Scénarios Développés sur Mesure :\nScan OWASP, HTTP Flood asynchrone, Slowloris par sockets TCP partiels, et Chaos de dégradation.\n\n• Postulat Réaliste :\nLe WAF arrête le grossier, la résilience prend le relais sur l'insidieux.");
  s6c2.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(13).setBold(true).setForegroundColor(COLOR_RED);

  setNotes(s6, "[CYBERSÉCURITÉ - 2:45 à 3:15]\nDéfense en profondeur à double détente : Première détente, le WAF Nginx qui bloque les scanners en 403 et applique un rate limiting en 429. Deuxième détente : si une attaque sophistiquée passe (Slowloris ou Chaos), le WAF est impuissant et notre IA prend le relais.");

  // -------------------------------------------------------------------------
  // SLIDE 7 : PILIER IA/DATA — AIOPS ISOLATION FOREST
  // -------------------------------------------------------------------------
  var s7 = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  s7.getBackground().setSolidFill(COLOR_BG);
  addHeader(s7, "Pilier IA / DATA : Détection Comportementale AIOps (Machine Learning)");

  var s7c1 = addCard(s7, 40, 85, 315, 290, COLOR_CARD);
  s7c1.getText().setText("Modèle Isolation Forest (Scikit-Learn)\n\n• Détection Non-Supervisée :\nPas de règles 'if/else' fixes. Isole les anomalies par partitionnement arborescent.\n\n• Baseline Nominale Entraînée :\nEntraîné sur 1 500 échantillons sains avec une contamination calibrée à 3%.\n\n• Ultra-Léger & Zéro GPU :\nInférence en moins de 5 ms sur CPU. Tourne directement en mémoire sur le PC Hôte.\n\n• Garde-fous Anti-Faux Positifs :\nIgnorer les micro-variations si latence < 150 ms et taux d'erreurs < 5%.");
  s7c1.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(13).setBold(true).setForegroundColor(COLOR_NAVY);

  var s7c2 = addCard(s7, 365, 85, 315, 290, COLOR_DARK_CARD, COLOR_BLUE);
  s7c2.getText().setText("Vecteur Télémétrique 4D Ingesté\n\n1. request_rate (req/s) :\nDébit réel calculé par dérivation différentielle.\n\n2. avg_latency_ms (ms) :\nLatence moyenne de traitement de l'API.\n\n3. error_rate_5xx (%) :\nRatio d'erreurs serveur par rapport aux requêtes.\n\n4. active_requests (connexions) :\nConnexions HTTP concurrentes actives sur le serveur.\n\nRÈGLE DE DÉCLENCHEMENT :\n2 anomalies consécutives confirmées (Score < 0) ➔ Émission Webhook immédiate au Moteur de Remédiation.");
  s7c2.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(13).setBold(true).setForegroundColor(COLOR_WHITE);

  setNotes(s7, "[MACHINE LEARNING - 3:15 à 3:45]\nPour l'IA : un modèle Isolation Forest non supervisé. Toutes les 3 secondes, il évalue un vecteur 4D : débit, latence, erreurs 5xx et requêtes actives. Deux anomalies consécutives déclenchent instantanément le webhook vers le moteur de remédiation.");

  // -------------------------------------------------------------------------
  // SLIDE 8 : LA CHAÎNE ZERO-TOUCH RECOVERY EN 5 ÉTAPES
  // -------------------------------------------------------------------------
  var s8 = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  s8.getBackground().setSolidFill(COLOR_BG);
  addHeader(s8, "Le Cœur de la Résilience : La Chaîne Zero-Touch en 5 Étapes");

  var zSteps = [
    { t: "T = 0s", s: "Attaque Red Team", d: "Attaque externe Slowloris ou Chaos contournant le WAF.", c: COLOR_RED },
    { t: "T + 3s", s: "Dégradation", d: "Latence > 1000ms et erreurs 500. Dashboard à l'orange.", c: COLOR_AMBER },
    { t: "T + 6s", s: "Détection AIOps", d: "Confirmation ML sur 2 cycles et émission du webhook.", c: COLOR_BLUE },
    { t: "T + 8s", s: "Remédiation K8s", d: "Rollout restart progressif des pods ou relance conteneur.", c: COLOR_NAVY },
    { t: "T + 18s", s: "Preuve Reprise", d: "Paiement réel validé (201 Created). Voyant vert certifié !", c: COLOR_GREEN }
  ];
  for (var i = 0; i < zSteps.length; i++) {
    var zx = 40 + i * 130;
    var zCard = addCard(s8, zx, 85, 120, 235, COLOR_CARD, zSteps[i].c);
    zCard.getText().setText(zSteps[i].t + "\n" + zSteps[i].s + "\n\n" + zSteps[i].d);
    zCard.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(12).setBold(true).setForegroundColor(zSteps[i].c);
    zCard.getText().getParagraphs()[1].getTextStyle().setFontFamily("Montserrat").setFontSize(10).setBold(true).setForegroundColor(COLOR_NAVY);
  }

  var zBot = addCard(s8, 40, 330, 640, 45, COLOR_CARD, COLOR_GREEN);
  zBot.getText().setText("RÉSULTAT CHIFFRÉ : RTO CONSTATÉ < 20 SECONDES — ZÉRO INTERVENTION HUMAINE REQUISE.\nL'ensemble du cycle incident-détection-reprise-validation s'exécute de façon autonome en direct devant le jury.");
  zBot.getText().getTextStyle().setFontFamily("Montserrat").setFontSize(10).setBold(true).setForegroundColor(COLOR_GREEN);

  setNotes(s8, "[RÉSUMÉ ZERO-TOUCH - 3:45 à 4:15]\nVoici la chronologie de notre chaîne autonome : en moins de 20 secondes montre en main, l'attaque est lancée, détectée par l'IA, le pod est redémarré proprement sous K8s, et un paiement de test valide le retour à la normale sans qu'aucun membre de l'équipe n'intervienne.");

  // -------------------------------------------------------------------------
  // SLIDE 9 : MATRICE DES 5 ATTAQUES RED TEAM
  // -------------------------------------------------------------------------
  var s9 = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  s9.getBackground().setSolidFill(COLOR_BG);
  addHeader(s9, "Matrice Red Team vs Blue Team : Les 5 Scénarios Éprouvés");

  var s9Card = addCard(s9, 40, 85, 640, 290, COLOR_CARD);
  s9Card.getText().setText("Synthèse des 5 Attaques & Réactions Défensives\n\n1. Scan OWASP (User-Agent sqlmap / nikto) ➔ Bloqué net par le WAF (HTTP 403 Forbidden). Backend non sollicité.\n\n2. HTTP Flood Volumétrique (POST /payments) ➔ Rate-limité par le WAF (HTTP 429). Si persistant : scale HPA de 3 à 8 réplicas K8s.\n\n3. Slowloris (Sockets TCP bruts incomplets) ➔ Passe le WAF (faille démo) ➔ Sature les sockets ➔ ML AIOps détecte latence ➔ Rollout restart Zero-Touch.\n\n4. Chaos & Dégradation API (POST /chaos) ➔ Passe le WAF ➔ 65% erreurs 500 et 1.2s latence ➔ Isolation Forest alerte ➔ Reprise autonome.\n\n5. Crash Brutal du Pod (POST /chaos/crash) ➔ Sortie conteneur (exit 1) ➔ Sondes Liveness K8s recréent le conteneur en self-healing physique.");
  s9Card.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(13).setBold(true).setForegroundColor(COLOR_NAVY);

  setNotes(s9, "[MATRICE RED TEAM - 4:15 à 4:45]\nNous couvrons 5 attaques : les deux premières valident la prévention WAF et l'élasticité HPA. Les trois suivantes prouvent la cyber-résilience autonome face à l'asphyxie logicielle ou au crash physique.");

  // -------------------------------------------------------------------------
  // SLIDE 10 : LE CLIP CHRONO (60 SECONDES SANS COUPE)
  // -------------------------------------------------------------------------
  var s10 = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  s10.getBackground().setSolidFill(COLOR_BG);
  addHeader(s10, "Le Clip Chrono : 60 Secondes en Continu sans Coupe");

  var clipBlocks = [
    { t: "00:00 - 00:12", s: "État Nominal", d: "• Terminal actif\n• Transactions réussies\n• Dashboard SOC au vert\n• Latence ~ 25 ms", c: COLOR_GREEN },
    { t: "00:12 - 00:28", s: "Attaque Red Team", d: "• Lancement PC Attaquant\n• Trafic hostile injecté\n• Dashboard à l'orange\n• Pic de latence visible", c: COLOR_RED },
    { t: "00:28 - 00:46", s: "Auto-Guérison", d: "• Alerte ML AIOps\n• Webhook vers reprise\n• K8s recrée les pods\n• Zéro action humaine", c: COLOR_BLUE },
    { t: "00:46 - 01:00", s: "Preuve Reprise", d: "• Service de retour\n• Nouveau paiement réussi\n• Voyant vert certifié\n• Reprise validée !", c: COLOR_NAVY }
  ];
  for (var i = 0; i < clipBlocks.length; i++) {
    var cx = 40 + i * 162;
    var cCard = addCard(s10, cx, 85, 152, 235, COLOR_CARD, clipBlocks[i].c);
    cCard.getText().setText(clipBlocks[i].t + "\n" + clipBlocks[i].s + "\n\n" + clipBlocks[i].d);
    cCard.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(12).setBold(true).setForegroundColor(clipBlocks[i].c);
    cCard.getText().getParagraphs()[1].getTextStyle().setFontFamily("Montserrat").setFontSize(11).setBold(true).setForegroundColor(COLOR_NAVY);
  }

  var cBot = addCard(s10, 40, 330, 640, 45, COLOR_DARK_CARD, COLOR_ACCENT);
  cBot.getText().setText("CONFORMITÉ NATIONALE DU CLIP CHRONO (15 POINTS NATIONAUX / 4 POINTS LOCAUX) :\nFormat MP4 strict, exactement 60 secondes, capture continue sans coupe, horodatage visible et titrage dynamique.");
  cBot.getText().getTextStyle().setFontFamily("Montserrat").setFontSize(9).setForegroundColor(COLOR_WHITE);

  setNotes(s10, "[CLIP CHRONO - 4:45 à 5:15]\nNotre vidéo respecte scrupuleusement les exigences : exactement 60 secondes en continu, sans coupe, démontrant l'état avant, pendant et après l'incident avec la certification par transaction.");

  // -------------------------------------------------------------------------
  // SLIDE 11 : PILIER GOUVERNANCE — EBIOS RM
  // -------------------------------------------------------------------------
  var s11 = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  s11.getBackground().setSolidFill(COLOR_BG);
  addHeader(s11, "Pilier GOUVERNANCE : Démarche d'Analyse de Risques EBIOS RM");

  var ebiosData = [
    { a: "Atelier 1", t: "Cadrage", d: "• Valeur métier : Traitement des paiements.\n• Biens supports : API FastAPI, Postgres, Ingress WAF.\n• Événements redoutés : Indisponibilité > 1 min." },
    { a: "Atelier 2", t: "Sources de Risques", d: "• Cybercriminels (extorsion).\n• Concurrents déloyaux.\n• Hacktivistes ciblant les infrastructures financières." },
    { a: "Atelier 3", t: "Scénarios Stratégiques", d: "• DDoS volumétrique sur l'API.\n• Asphyxie insidieuse (Slowloris).\n• Compromission d'administration SOC." },
    { a: "Atelier 4", t: "Scénarios Opérationnels", d: "• Saturation de descripteurs TCP.\n• Injection d'erreurs 500 par payload corrompu.\n• Exfiltration de données simulées." },
    { a: "Atelier 5", t: "Traitement du Risque", d: "• Prévention : WAF L7 durci.\n• Résilience : AIOps & Zero-Touch.\n• Risque résiduel maîtrisé et documenté." }
  ];
  for (var i = 0; i < ebiosData.length; i++) {
    var ex = 40 + i * 130;
    var eCard = addCard(s11, ex, 85, 120, 290, COLOR_CARD);
    eCard.getText().setText(ebiosData[i].a + "\n" + ebiosData[i].t + "\n\n" + ebiosData[i].d);
    eCard.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(12).setBold(true).setForegroundColor(COLOR_NAVY);
    eCard.getText().getParagraphs()[1].getTextStyle().setFontFamily("Montserrat").setFontSize(9).setBold(true).setForegroundColor(COLOR_ACCENT);
  }

  setNotes(s11, "[GOUVERNANCE EBIOS RM - 5:15 à 5:45]\nNous avons structuré notre gestion des risques selon la méthodologie EBIOS RM en 5 ateliers. Le démonstrateur concrétise directement le traitement des risques de l'Atelier 5 grâce au couplage WAF et remédiation Zero-Touch.");

  // -------------------------------------------------------------------------
  // SLIDE 12 : CONFORMITÉ DORA & DIRECTIVE NIS2
  // -------------------------------------------------------------------------
  var s12 = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  s12.getBackground().setSolidFill(COLOR_BG);
  addHeader(s12, "Gouvernance : Alignement Règlement DORA & Directive NIS2");

  var s12c1 = addCard(s12, 40, 85, 315, 290, COLOR_CARD);
  s12c1.getText().setText("Règlement DORA (Secteur Financier UE)\n\n• Article 6 — Gestion du risque TIC :\nArchitecture résiliente et tolérante aux pannes avec redondance active (3 réplicas API + HPA).\n\n• Article 17 — Notification des incidents majeurs :\nTélémétrie temps réel et génération de logs auditables Loki.\n\n• Article 24 — Tests de résilience opérationnelle :\nCampagnes régulières d'attaques Red Team et Chaos Engineering.\n\n• Article 28 — Risques liés aux tiers :\nFiltrage et étanchéité stricts des flux API via WAF L7.");
  s12c1.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(13).setBold(true).setForegroundColor(COLOR_NAVY);

  var s12c2 = addCard(s12, 365, 85, 315, 290, COLOR_CARD_SOFT);
  s12c2.getText().setText("Directive NIS2 & Hygiène ANSSI\n\n• Entités Essentielles / Importantes :\nOpérateurs de paiement relevant des critères de haute criticité NIS2.\n\n• Délais de Déclaration Stricts :\nSignalement à l'ANSSI sous 24h (alerte précoce) et 72h (rapport détaillé).\n\n• Cloisonnement & Moindre Privilège :\nPrincipe Zero-Trust : jetons JWT pour l'administration SOC, ports internes isolés à 127.0.0.1.\n\n• Responsabilité de la Gouvernance :\nAuditabilité complète du PCA/PRA et des résultats de cyber-résilience.");
  s12c2.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(13).setBold(true).setForegroundColor(COLOR_NAVY);

  setNotes(s12, "[DORA & NIS2 - 5:45 à 6:15]\nConformité totale avec les règlements européens : DORA Art. 6 (redondance) et Art. 24 (tests de pénétration), et NIS2 sur la traçabilité intégrale et le moindre privilège.");

  // -------------------------------------------------------------------------
  // SLIDE 13 : STRATÉGIE PCA / PRA & RECOMMANDATIONS
  // -------------------------------------------------------------------------
  var s13 = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  s13.getBackground().setSolidFill(COLOR_BG);
  addHeader(s13, "PCA / PRA Métier & Recommandations Stratégiques");

  var s13c1 = addCard(s13, 40, 85, 315, 290, COLOR_DARK_CARD, COLOR_ACCENT);
  s13c1.getText().setText("Métriques Démontrées du PCA / PRA\n\n• RTO Constaté (Temps de Reprise) :\n< 20 secondes (contre 15 à 45 minutes en manuel, gain x50).\n\n• RPO Constaté (Perte de Données) :\n= 0 seconde (persistance PostgreSQL ACID & idempotence des ordres de paiement).\n\n• Disponibilité Cible Démontrée :\n99.95 % (haute disponibilité assurée par multi-pods et auto-scaling HPA).");
  s13c1.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(13).setBold(true).setForegroundColor(COLOR_WHITE);

  var s13c2 = addCard(s13, 365, 85, 315, 290, COLOR_CARD);
  s13c2.getText().setText("Recommandations à la Direction Générale\n\n1. Généraliser l'AIOps en Production :\nÉtendre l'Isolation Forest à toutes les passerelles bancaires et microservices de facturation.\n\n2. Architecture Multi-Régions :\nRépliquer les clusters Kubernetes sur 2 datacenters distincts en actif-actif.\n\n3. Chaos Engineering Continu en CI/CD :\nInjecter automatiquement des pannes contrôlées à chaque release pour tester la résilience.\n\n4. Gestionnaire de Secrets d'Entreprise :\nIntégrer HashiCorp Vault pour la rotation dynamique des certificats et des secrets.");
  s13c2.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(13).setBold(true).setForegroundColor(COLOR_NAVY);

  setNotes(s13, "[PCA/PRA & RECOMMANDATIONS - 6:15 à 6:45]\nNotre RTO passe de plus de 30 minutes à moins de 20 secondes. Notre RPO est nul. Recommandations : déploiement multi-régions actif-actif, intégration du Chaos Testing en CI/CD et généralisation de l'AIOps.");

  // -------------------------------------------------------------------------
  // SLIDE 14 : BILAN DU CONSORTIUM & RÉPARTITION
  // -------------------------------------------------------------------------
  var s14 = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  s14.getBackground().setSolidFill(COLOR_BG);
  addHeader(s14, "Bilan du Sprint : Synergie d'Équipe & Maîtrise Technique");

  var teamData = [
    { n: "Théo", r: "K8s & Infra", d: "• Helm Chart & manifests K8s\n• Kind Ingress & HPA\n• Ansible & déploiement" },
    { n: "Mael", r: "Dev Métier", d: "• FastAPI Payment API\n• PostgreSQL transactionnel\n• Microservice Auth JWT" },
    { n: "Flora", r: "Cybersécurité", d: "• WAF Nginx durci L7\n• Règles anti-scanners & rate limit\n• Console Red Team" },
    { n: "Fely", r: "IA & AIOps", d: "• Modèle Isolation Forest\n• Baseline nominale\n• Webhook de remédiation" },
    { n: "Aymeric", r: "Gouvernance", d: "• EBIOS RM (5 ateliers)\n• Conformité DORA & NIS2\n• Élaboration PCA/PRA" }
  ];
  for (var i = 0; i < teamData.length; i++) {
    var tx = 40 + i * 130;
    var tCard = addCard(s14, tx, 85, 120, 235, COLOR_CARD);
    tCard.getText().setText(teamData[i].n + "\n" + teamData[i].r + "\n\n" + teamData[i].d);
    tCard.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(12).setBold(true).setForegroundColor(COLOR_NAVY);
    tCard.getText().getParagraphs()[1].getTextStyle().setFontFamily("Montserrat").setFontSize(9).setBold(true).setForegroundColor(COLOR_ACCENT);
  }

  var tBot = addCard(s14, 40, 330, 640, 45, COLOR_DARK_CARD, COLOR_ACCENT);
  tBot.getText().setText("MAÎTRISE COMPLÈTE DU CODE & USAGE DE L'IA GÉNÉRATIVE (AXE 5 DU SUJET) :\n100% du code produit et généré avec assistance IA a été revu, durci, testé unitairement (pytest) et validé en conditions réelles.");
  tBot.getText().getTextStyle().setFontFamily("Montserrat").setFontSize(9).setForegroundColor(COLOR_WHITE);

  setNotes(s14, "[BILAN DU CONSORTIUM - 6:45 à 7:15]\nSprint commando de quatre jours. Chacun a assumé la responsabilité d'un pilier tout en conservant une vision d'ensemble. Tout le code a été revu, durci et validé par notre suite de tests automatisés pytest.");

  // -------------------------------------------------------------------------
  // SLIDE 15 : DÉMONSTRATION EN DIRECT & QUESTIONS / RÉPONSES
  // -------------------------------------------------------------------------
  var s15 = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  s15.getBackground().setSolidFill(COLOR_NAVY);
  addCard(s15, 30, 30, 660, 340, COLOR_NAVY, COLOR_ACCENT);

  var tb15 = s15.insertTextBox("DÉMONSTRATION EN DIRECT\nPassage au Live (3 min) & Session d'Échanges avec le Jury", 50, 45, 620, 70);
  tb15.getText().getTextStyle().setFontFamily("Montserrat");
  tb15.getText().getParagraphs()[0].getTextStyle().setFontSize(26).setBold(true).setForegroundColor(COLOR_WHITE);
  tb15.getText().getParagraphs()[1].getTextStyle().setFontSize(13).setForegroundColor(COLOR_BG);

  var accessLinks = [
    { t: "Terminal Bancaire Client", u: "http://localhost:3000", d: "Accès public simulant le parcours d'achat client." },
    { t: "Supervision SOC", u: "http://localhost:3000/supervision", d: "Accès protégé JWT : métriques AIOps, pods et logs." },
    { t: "Console Red Team", u: "http://localhost:3001", d: "PC Attaquant externe : déclenchement des 5 attaques." }
  ];
  for (var i = 0; i < accessLinks.length; i++) {
    var ax = 50 + i * 210;
    var aCard = s15.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE, ax, 130, 200, 130);
    aCard.getFill().setSolidFill('#302858');
    aCard.getBorder().setSolidFill(COLOR_ACCENT);
    aCard.getText().setText(accessLinks[i].t + "\n" + accessLinks[i].u + "\n\n" + accessLinks[i].d);
    aCard.getText().getParagraphs()[0].getTextStyle().setFontFamily("Montserrat").setFontSize(11).setBold(true).setForegroundColor(COLOR_WHITE);
    aCard.getText().getParagraphs()[1].getTextStyle().setFontFamily("Montserrat").setFontSize(9).setBold(true).setForegroundColor(COLOR_GREEN);
    aCard.getText().getParagraphs()[2].getTextStyle().setFontFamily("Montserrat").setFontSize(8).setForegroundColor(COLOR_BG);
  }

  var tbEnd = s15.insertTextBox("« PROJECT RESILIENCE-ALPHA : La cyber-résilience ne se promet pas, elle se démontre. »\nMerci pour votre attention. Nous lançons à présent le scénario d'attaque en direct !", 50, 275, 620, 60);
  tbEnd.getText().getTextStyle().setFontFamily("Montserrat");
  tbEnd.getText().getParagraphs()[0].getTextStyle().setFontSize(12).setItalic(true).setForegroundColor(COLOR_ACCENT);
  tbEnd.getText().getParagraphs()[1].getTextStyle().setFontSize(14).setBold(true).setForegroundColor(COLOR_WHITE);

  setNotes(s15, "[TRANSITION DÉMO LIVE & QUESTIONS JURY]\nMerci pour votre écoute. Nous passons immédiatement à la démonstration en direct : sur le PC Hôte, nous observons le terminal de paiement et le dashboard SOC. Depuis le PC Attaquant, nous déclenchons l'attaque. Observez la détection instantanée de l'Isolation Forest et la reprise Zero-Touch certifiée par une transaction. Nous sommes à votre disposition pour vos questions !");

  Logger.log("Les 15 diapositives ont été générées avec succès !");
}
