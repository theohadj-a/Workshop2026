import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# --- COLOR PALETTE (Charte EPSI Resilience-Alpha) ---
COLOR_BG = RGBColor(228, 230, 243)          # #E4E6F3 - Fond diapo doux
COLOR_NAVY = RGBColor(38, 30, 72)           # #261E48 - Ecriture / Titres / Brand
COLOR_ACCENT = RGBColor(161, 166, 212)      # #A1A6D4 - Fond rectangle / Bordures
COLOR_CARD_BG = RGBColor(255, 255, 255)     # #FFFFFF - Cartes blanches pour lisibilité
COLOR_CARD_SOFT = RGBColor(241, 242, 250)   # #F1F2FA - Cartes grises très claires
COLOR_DARK_CARD = RGBColor(38, 30, 72)      # #261E48 - Cartes sombres contrastées
COLOR_MUTED = RGBColor(100, 100, 130)       # #646482 - Texte secondaire / labels
COLOR_RED = RGBColor(220, 38, 38)           # #DC2626 - Alerte Red Team / Crash
COLOR_GREEN = RGBColor(22, 163, 74)         # #16A34A - Reprise / Succès transaction
COLOR_BLUE = RGBColor(37, 99, 235)          # #2563EB - AIOps / Détection
COLOR_AMBER = RGBColor(217, 119, 6)         # #D97706 - Warning / Dégradation

FONT_TITLE = "Montserrat"
FONT_BODY = "Montserrat"

def create_deck(output_path: str):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]  # Blank slide

    def set_slide_background(slide, color=COLOR_BG):
        bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = color
        bg_shape.line.fill.background()
        return bg_shape

    def add_header(slide, title: str, category: str = "WORKSHOP M2 EPSI • PROJECT RESILIENCE-ALPHA"):
        # Category / Overline
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_top = tf_cat.margin_right = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.name = FONT_TITLE
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_ACCENT

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.65))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.name = FONT_TITLE
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_NAVY

    def add_card(slide, left, top, width, height, bg_color=COLOR_CARD_BG, border_color=COLOR_ACCENT, border_width=1):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(border_width)
        else:
            shape.line.fill.background()
        return shape

    def set_notes(slide, notes_text: str):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text.strip()

    # =========================================================================
    # SLIDE 1 : TITRE & CONSORTIUM
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, COLOR_NAVY)

    # Decorative header card
    add_card(s1, 0.8, 0.8, 11.733, 5.9, bg_color=COLOR_NAVY, border_color=COLOR_ACCENT, border_width=2)

    # Badge
    b1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.3), Inches(1.3), Inches(4.5), Inches(0.45))
    b1.fill.solid()
    b1.fill.fore_color.rgb = COLOR_ACCENT
    b1.line.fill.background()
    p = b1.text_frame.paragraphs[0]
    p.text = "DIRECTION NATIONALE DE LA SÛRETÉ NUMÉRIQUE"
    p.font.name = FONT_TITLE
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY
    p.alignment = PP_ALIGN.CENTER

    # Title box
    tb = s1.shapes.add_textbox(Inches(1.3), Inches(2.0), Inches(10.7), Inches(2.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "PROJECT RESILIENCE-ALPHA"
    p1.font.name = FONT_TITLE
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(255, 255, 255)

    p2 = tf.add_paragraph()
    p2.text = "Cyber-Résilience Autonome & Reprise sans Intervention Humaine (Zero-Touch Recovery)"
    p2.font.name = FONT_BODY
    p2.font.size = Pt(16)
    p2.font.italic = True
    p2.font.color.rgb = COLOR_BG

    p3 = tf.add_paragraph()
    p3.text = "« Tout système finit par tomber. La vraie question : le vôtre saura-t-il se relever seul ? »"
    p3.font.name = FONT_BODY
    p3.font.size = Pt(13)
    p3.font.color.rgb = COLOR_ACCENT

    # Team members row
    team_members = [
        ("Théo", "Architecture & Orchestration K8s"),
        ("Mael", "Développement API & Microservices"),
        ("Flora", "Cybersécurité, WAF & Red Team"),
        ("Fely", "AIOps Machine Learning & Détection"),
        ("Aymeric", "Gouvernance EBIOS RM, DORA & PCA")
    ]
    card_w = 2.05
    gap = 0.12
    start_x = 1.3
    y_pos = 4.8
    for i, (name, role) in enumerate(team_members):
        cx = start_x + i * (card_w + gap)
        add_card(s1, cx, y_pos, card_w, 1.4, bg_color=RGBColor(48, 40, 88), border_color=COLOR_ACCENT)
        box = s1.shapes.add_textbox(Inches(cx + 0.1), Inches(y_pos + 0.15), Inches(card_w - 0.2), Inches(1.1))
        tf = box.text_frame
        tf.word_wrap = True
        p_n = tf.paragraphs[0]
        p_n.text = name
        p_n.font.name = FONT_TITLE
        p_n.font.size = Pt(14)
        p_n.font.bold = True
        p_n.font.color.rgb = RGBColor(255, 255, 255)
        
        p_r = tf.add_paragraph()
        p_r.text = role
        p_r.font.name = FONT_BODY
        p_r.font.size = Pt(9.5)
        p_r.font.color.rgb = COLOR_BG

    set_notes(s1, """[PITCH D'OUVERTURE - 0:00 à 0:45]
Bonjour à tous, membres du jury.
À l'automne 2026, la question n'est plus de savoir si un système d'information critique va subir une cyberattaque ou une défaillance majeure, mais à quelle vitesse et avec quel degré d'autonomie il est capable de s'en relever.
Face à la multiplication des indisponibilités d'infrastructures de paiement et aux interventions manuelles lentes et coûteuses, notre consortium — composé de Théo, Mael, Flora, Fely et Aymeric — a conçu et implémenté PROJECT RESILIENCE-ALPHA.
Notre mission : prouver qu'une plateforme transactionnelle critique peut encaisser une attaque Red Team en conditions réelles, détecter l'anomalie par Machine Learning, et déclencher une remédiation Zero-Touch 100% autonome validée par une nouvelle transaction bancaire réussie.
Voici comment nous avons relevé ce défi.""")

    # =========================================================================
    # SLIDE 2 : CONTEXTE, DÉFI & EXIGENCES CRITIQUES
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Le Défi National : Continuité Métier & Zero-Touch Recovery")

    # 3 Cards Layout
    # Card 1: Contexte Métier
    add_card(s2, 0.8, 1.5, 3.7, 5.2)
    b = s2.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(3.3), Inches(4.8))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Contexte Bancaire Critique"
    p.font.name = FONT_TITLE
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    items1 = [
        "Plateforme transactionnelle soumise à des incidents récurrents.",
        "Interventions manuelles lentes, complexes et difficilement reproductibles.",
        "Perte financière immédiate, rupture de confiance clients et partenaires.",
        "Obligations de conformité renforcées (DORA & NIS2) imposant une résilience démontrée."
    ]
    for it in items1:
        p = tf.add_paragraph()
        p.text = "• " + it
        p.font.name = FONT_BODY
        p.font.size = Pt(11.5)
        p.font.color.rgb = COLOR_NAVY

    # Card 2: Le Défi Technique
    add_card(s2, 4.8, 1.5, 3.7, 5.2)
    b = s2.shapes.add_textbox(Inches(5.0), Inches(1.7), Inches(3.3), Inches(4.8))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. Le Défi DNSN"
    p.font.name = FONT_TITLE
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    items2 = [
        "SI de paiement conteneurisé complet (Front React, API REST, Auth JWT, PostgreSQL).",
        "Attaque réelle exécutée depuis un PC Attaquant physiquement découplé.",
        "Détection par Machine Learning (Isolation Forest) et non simples seuils fixes.",
        "Remédiation autonome : auto-guérison sans intervention humaine (Zero-Touch)."
    ]
    for it in items2:
        p = tf.add_paragraph()
        p.text = "• " + it
        p.font.name = FONT_BODY
        p.font.size = Pt(11.5)
        p.font.color.rgb = COLOR_NAVY

    # Card 3: La Règle d'Or & Preuve
    add_card(s2, 8.8, 1.5, 3.7, 5.2, bg_color=COLOR_DARK_CARD, border_color=COLOR_RED)
    b = s2.shapes.add_textbox(Inches(9.0), Inches(1.7), Inches(3.3), Inches(4.8))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3. Règle d'Évaluation & Preuve"
    p.font.name = FONT_TITLE
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    items3 = [
        ("Zéro intervention humaine :", "Toute action manuelle pendant la démonstration entraîne immédiatement 0/5 sur l'axe remédiation."),
        ("Preuve par la transaction :", "Un redémarrage de pod ne suffit pas. Le système doit émettre un nouveau paiement réussi après reprise."),
        ("Visibilité continue :", "État du service affiché en temps réel : avant, pendant et après l'incident.")
    ]
    for title, desc in items3:
        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_ACCENT
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = RGBColor(255, 255, 255)

    set_notes(s2, """[CADRAGE STRATÉGIQUE - 0:45 à 1:15]
Le cahier des charges posé par la Direction Nationale de la Sûreté Numérique est sans ambiguïté :
Dans un secteur bancaire hautement réglementé, l'indisponibilité se chiffre en milliers d'euros par minute. Relancer un service à la main est anachronique et dangereux.
Mais attention : la règle d'or de ce workshop pénalise toute intervention humaine d'un 0 éliminatoire.
De plus, un conteneur qui affiche un statut 'Running' ne prouve rien si la logique métier est bloquée. C'est pourquoi notre moteur valide la reprise par la preuve ultime : l'exécution automatisée d'une transaction bancaire réelle après l'incident.""")

    # =========================================================================
    # SLIDE 3 : ARCHITECTURE GLOBALE & LES 5 PILIERS INTERCONNECTÉS
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Architecture Globale : L'Interconnexion des 5 Piliers")

    # 5 Pillars Horizontal Layout
    pillars = [
        ("DEV", "Microservices & UI", [
            "FastAPI Payment API",
            "Auth Service JWT Bearer",
            "Dashboard React + Tailwind",
            "PostgreSQL transactionnel",
            "Remediation Engine"
        ], COLOR_NAVY),
        ("INFRA", "Kubernetes & Observabilité", [
            "Helm Chart officiel paramétrable",
            "3 réplicas API + HPA élastique",
            "NetworkPolicies & Kind Ingress",
            "Prometheus (scrape 1s)",
            "Grafana & Loki centralisé"
        ], COLOR_NAVY),
        ("CYBER", "Défense en Profondeur", [
            "WAF Nginx durci L7",
            "Anti-Scanner OWASP (403)",
            "Rate Limiting 5 req/s (429)",
            "Console Red Team découplée",
            "Cloisonnement réseau strict"
        ], COLOR_RED),
        ("IA / DATA", "AIOps & RAG", [
            "Isolation Forest Scikit-learn",
            "Vecteur 4D temps réel",
            "Détection non supervisée",
            "Webhook d'alerte instantané",
            "Assistant local Ollama/LangChain"
        ], COLOR_BLUE),
        ("TRANSFORMATION", "Gouvernance & Risques", [
            "Analyse des risques EBIOS RM",
            "Conformité DORA (Art. 6, 17, 24)",
            "Directive NIS2 & Hygiène ANSSI",
            "PCA/PRA opérationnel",
            "RTO cible < 30s | RPO = 0"
        ], COLOR_NAVY),
    ]

    col_w = 2.22
    col_gap = 0.15
    for i, (name, subtitle, points, border_col) in enumerate(pillars):
        cx = 0.8 + i * (col_w + col_gap)
        add_card(s3, cx, 1.5, col_w, 4.4, border_color=border_col, border_width=2)
        
        # Header banner inside card
        banner = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(cx), Inches(1.5), Inches(col_w), Inches(0.8))
        banner.fill.solid()
        banner.fill.fore_color.rgb = border_col
        banner.line.fill.background()
        tf_b = banner.text_frame
        tf_b.word_wrap = True
        p1 = tf_b.paragraphs[0]
        p1.text = name
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = RGBColor(255, 255, 255)
        p1.alignment = PP_ALIGN.CENTER
        p2 = tf_b.add_paragraph()
        p2.text = subtitle
        p2.font.name = FONT_BODY
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = COLOR_BG
        p2.alignment = PP_ALIGN.CENTER

        # Bullet points
        b = s3.shapes.add_textbox(Inches(cx + 0.1), Inches(2.4), Inches(col_w - 0.2), Inches(3.4))
        tf = b.text_frame
        tf.word_wrap = True
        for pt_idx, pt in enumerate(points):
            p = tf.paragraphs[0] if pt_idx == 0 else tf.add_paragraph()
            p.text = "✓ " + pt
            p.font.name = FONT_BODY
            p.font.size = Pt(9.5)
            p.font.color.rgb = COLOR_NAVY

    # Bottom workflow connector card
    add_card(s3, 0.8, 6.05, 11.733, 0.95, bg_color=COLOR_DARK_CARD, border_color=COLOR_ACCENT)
    b_flow = s3.shapes.add_textbox(Inches(1.0), Inches(6.12), Inches(11.333), Inches(0.8))
    tf_f = b_flow.text_frame
    tf_f.word_wrap = True
    p_f = tf_f.paragraphs[0]
    p_f.text = "CHAÎNE D'INTERCONNEXION CONTINUE : "
    p_f.font.name = FONT_TITLE
    p_f.font.size = Pt(10.5)
    p_f.font.bold = True
    p_f.font.color.rgb = COLOR_ACCENT
    p_f2 = tf_f.add_paragraph()
    p_f2.text = "PC Attaquant (Red Team) ➔ WAF Nginx L7 ➔ API Paiement & K8s ➔ Métriques Prometheus ➔ Détecteur ML AIOps ➔ Webhook Remédiation ➔ Validation Transactionnelle."
    p_f2.font.name = FONT_BODY
    p_f2.font.size = Pt(10.5)
    p_f2.font.color.rgb = RGBColor(255, 255, 255)

    set_notes(s3, """[COHÉRENCE D'ARCHITECTURE - 1:15 à 1:45]
Chacun des 5 domaines requis par le référentiel national n'est pas une brique isolée : ils sont intimement interconnectés au cœur de notre chaîne de valeur.
Le pilier DEV fournit les microservices et l'UI.
L'INFRAstructure assure l'orchestration résiliente sous Kubernetes avec Helm et la captation télémétrique Prometheus.
La CYBERSÉCURITÉ filtre les menaces évidentes au niveau WAF et challenge la résilience via notre console Red Team externe.
L'IA/DATA traite les signaux en continu via notre modèle non-supervisé Isolation Forest.
Enfin, la TRANSFORMATION garantit que chaque brique technique répond scrupuleusement aux impératifs d'EBIOS RM et des règlements NIS2 et DORA.""")

    # =========================================================================
    # SLIDE 4 : PILIER DEV — CŒUR MÉTIER & REMÉDIATION
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Pilier DEV : Architecture Microservices & Supervision SOC")

    # Left: Microservices Schema / Cards
    add_card(s4, 0.8, 1.5, 5.7, 5.5)
    b_dev = s4.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(5.1))
    tf_dev = b_dev.text_frame
    tf_dev.word_wrap = True
    p = tf_dev.paragraphs[0]
    p.text = "Microservices Conteneurisés Métier"
    p.font.name = FONT_TITLE
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    dev_points = [
        ("payment-api (Python FastAPI) :", "API transactionnelle asynchrone, traitement des ordres de paiement, écriture PostgreSQL, endpoints /health et /metrics Prometheus."),
        ("auth-service (Microservice JWT) :", "Authentification forte RBAC (Admin SOC vs Analyste Opérateur). Cloisonnement strict des actions de remédiation par token Bearer."),
        ("remediation-engine :", "Cerveau d'auto-guérison. Reçoit les alertes du ML, communique avec l'API Kubernetes pour redémarrer les pods défaillants, puis certifie la reprise."),
        ("dashboard-ui (React + Tailwind) :", "Interface web unifiée : terminal de paiement public pour simuler le flux client, et console de supervision SOC temps réel.")
    ]
    for title, desc in dev_points:
        p_t = tf_dev.add_paragraph()
        p_t.text = "• " + title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_NAVY
        p_d = tf_dev.add_paragraph()
        p_d.text = "  " + desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = COLOR_MUTED

    # Right: Focus Remédiation & Preuve
    add_card(s4, 6.8, 1.5, 5.733, 5.5, bg_color=COLOR_CARD_SOFT)
    b_rem = s4.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.333), Inches(5.1))
    tf_rem = b_rem.text_frame
    tf_rem.word_wrap = True
    p = tf_rem.paragraphs[0]
    p.text = "Le Moteur de Remédiation & Preuve Métier"
    p.font.name = FONT_TITLE
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    rem_items = [
        ("Surveillance Native K8s (Niveau 1) :", "Sondes Liveness & Readiness intégrées. En cas de crash physique (OOMKilled, Error), K8s relance immédiatement le conteneur."),
        ("Réaction Intelligente ML (Niveau 2) :", "En cas d'asphyxie sans crash (Slowloris, fuite de mémoire, injection de chaos), le moteur ordonne un rollout restart progressif sans coupure."),
        ("La Preuve par la Transaction :", "Dès la notification de retour au vert, le module verifier.py injecte une requête POST /api/v1/payments avec un montant aléatoire et vérifie le code 201 Created."),
        ("Contrôle d'Accès SOC Sécurisé :", "Conforme DORA : les commandes de remédiation ne sont pas ouvertes au réseau public. Seul l'administrateur authentifié peut forcer un cycle.")
    ]
    for title, desc in rem_items:
        p_t = tf_rem.add_paragraph()
        p_t.text = "➔ " + title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_NAVY
        p_d = tf_rem.add_paragraph()
        p_d.text = "  " + desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = COLOR_NAVY

    set_notes(s4, """[EXPLICATION DÉVELOPPEMENT - 1:45 à 2:15]
Côté développement, nous avons fait le choix de microservices légers et performants en FastAPI pour le backend et React/Tailwind pour le frontend.
Deux éléments majeurs caractérisent notre implémentation :
D'abord, le cloisonnement des privilèges. Suivant les préceptes de DORA, nous avons créé un microservice d'authentification dédié. L'accès à la supervision et aux déclenchements manuels exige un jeton JWT Bearer chiffré.
Ensuite, le composant verifier.py au sein de notre moteur de remédiation. Dès que le redémarrage d'un réplica est achevé, il transmet une transaction synthétique de test. Si elle réussit, la reprise est certifiée et journalisée.""")

    # =========================================================================
    # SLIDE 5 : PILIER INFRA — KUBERNETES, HELM & OBSERVABILITÉ
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Pilier INFRA : Déploiement Helm, Haute Disponibilité & Métriques")

    # 3 Column Cards
    col_w = 3.65
    gap = 0.38
    
    # Col 1: Helm & K8s
    add_card(s5, 0.8, 1.5, col_w, 5.5)
    b = s5.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(col_w - 0.4), Inches(5.1))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Orchestration K8s / Helm"
    p.font.name = FONT_TITLE
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    pts_k8s = [
        "Helm Chart officiel 'resilience-alpha' entièrement paramétrable (values.yaml).",
        "Haute disponibilité : 3 réplicas par défaut pour l'API de paiement.",
        "Kind Cluster avec Ingress Nginx mappé sur les ports 80/443 de la machine hôte.",
        "Scripts de build automatisés cross-plateformes (Linux, WSL2, macOS ARM)."
    ]
    for pt in pts_k8s:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = COLOR_NAVY

    # Col 2: Élasticité & Réseau
    add_card(s5, 0.8 + col_w + gap, 1.5, col_w, 5.5)
    b = s5.shapes.add_textbox(Inches(1.0 + col_w + gap), Inches(1.7), Inches(col_w - 0.4), Inches(5.1))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Élasticité & NetworkPolicy"
    p.font.name = FONT_TITLE
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    pts_net = [
        "Horizontal Pod Autoscaler (HPA) : passage dynamique de 3 à 8 réplicas en cas de saturation CPU (>70%).",
        "NetworkPolicies Kubernetes : isolation stricte entre pods.",
        "PostgreSQL et services internes accessibles uniquement par l'API métier.",
        "Playbooks Ansible d'automatisation des déploiements et des tests de santé."
    ]
    for pt in pts_net:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = COLOR_NAVY

    # Col 3: Observabilité
    add_card(s5, 0.8 + 2 * (col_w + gap), 1.5, col_w, 5.5)
    b = s5.shapes.add_textbox(Inches(1.0 + 2 * (col_w + gap)), Inches(1.7), Inches(col_w - 0.4), Inches(5.1))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Chaîne d'Observabilité"
    p.font.name = FONT_TITLE
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    pts_obs = [
        "Prometheus : scraping temps réel à haute fréquence (intervalle 1 seconde) sur /metrics.",
        "Métriques clés : payment_http_requests_total, payment_active_requests, latence moyenne.",
        "Grafana : dashboards visuels pour suivre le trafic nominal et les attaques.",
        "Loki : centralisation des logs WAF et API sans surconsommation mémoire."
    ]
    for pt in pts_obs:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = COLOR_NAVY

    set_notes(s5, """[EXPLICATION INFRASTRUCTURE - 2:15 à 2:45]
Côté infrastructure, nous avons industrialisé l'environnement au moyen d'un Helm Chart officiel.
Trois réplicas de l'API de paiement tournent en permanence derrière un Ingress Controller.
Si une attaque volumétrique survient, le Horizontal Pod Autoscaler (HPA) augmente automatiquement les instances jusqu'à 8 pods.
La chaîne d'observabilité repose sur Prometheus configuré pour scraper les métriques à haute fréquence (1 seconde). C'est ce flux télémétrique direct qui nourrit en temps réel notre moteur d'intelligence artificielle.""")

    # =========================================================================
    # SLIDE 6 : PILIER CYBER — WAF L7 & RED TEAM EXTERNE
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Pilier CYBER : Défense en Profondeur WAF & Console Red Team")

    # Left: WAF Rules
    add_card(s6, 0.8, 1.5, 5.7, 5.5)
    b = s6.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(5.1))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Filtrage Applicatif WAF L7 (Nginx)"
    p.font.name = FONT_TITLE
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    waf_points = [
        ("1. Blocage Scanners OWASP (HTTP 403) :", "Détection immédiate des User-Agents malveillants réputés (sqlmap, nikto, nmap, dirbuster). La requête est rejetée net sans solliciter le backend."),
        ("2. Rate Limiting Sélectif (HTTP 429) :", "Plafond strict de 5 requêtes/seconde par adresse IP (burst de 10) sur /api/v1/payments. Bloque les attaques par flood de transactions."),
        ("3. Durcissement HTTP (Standards ANSSI) :", "En-têtes obligatoires injectés : X-Frame-Options DENY, X-Content-Type-Options nosniff, CSP stricte, protection XSS."),
        ("4. Résolution de la brèche WAF Bypass :", "Tous les microservices internes ont été restreints à 127.0.0.1. Tout flux externe transite obligatoirement par le WAF.")
    ]
    for title, desc in waf_points:
        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_NAVY
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = COLOR_MUTED

    # Right: Red Team Setup
    add_card(s6, 6.8, 1.5, 5.733, 5.5, bg_color=COLOR_CARD_SOFT, border_color=COLOR_RED)
    b = s6.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.333), Inches(5.1))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Console Attaquant & Red Team Découplée"
    p.font.name = FONT_TITLE
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_RED

    red_points = [
        ("Découplage Physique Strict :", "Module attaquant hébergé sur un second ordinateur distinct, connecté via le point d'accès Wi-Fi dédié RESILIENCE-G<n>."),
        ("Double Interface d'Attaque :", "Dashboard interactif Next.js (port 3001) avec feedback temps réel, et script CLI Python pour exécution scriptée."),
        ("Scénarios Développés sur Mesure :", "Scan de vulnérabilités, HTTP Flood asynchrone, Slowloris sockets TCP partiels, et injection de dégradation/latence (Chaos)."),
        ("Postulat Réaliste :", "Le WAF arrête les attaques grossières ; la cyber-résilience prend le relais sur les attaques évoluées non filtrables.")
    ]
    for title, desc in red_points:
        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_NAVY
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = COLOR_NAVY

    set_notes(s6, """[CYBERSÉCURITÉ & POSTURE DÉFENSIVE - 2:45 à 3:15]
En cybersécurité, notre philosophie a été d'adopter une défense en profondeur à double détente :
Première détente : le pare-feu applicatif Nginx. Il applique des règles strictes de réputation d'agents et de limitation de débit. Un attaquant qui lance un scan Nikto ou SQLmap est immédiatement stoppé avec un code 403. S'il tente d'inonder la route de paiement, il reçoit un 429.
Deuxième détente : que se passe-t-il si l'attaque est plus sophistiquée, comme une attaque Slowloris par maintien de sockets ou une dégradation logique interne ?
C'est précisément là que le WAF ne peut plus suffire, et que notre pilier Machine Learning intervient.""")

    # =========================================================================
    # SLIDE 7 : PILIER IA/DATA — AIOPS ISOLATION FOREST
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Pilier IA / DATA : Détection Comportementale AIOps (Machine Learning)")

    # 2 Columns Layout
    add_card(s7, 0.8, 1.5, 5.7, 5.5)
    b = s7.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(5.1))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Modèle Isolation Forest (Scikit-Learn)"
    p.font.name = FONT_TITLE
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    ml_points = [
        ("Détection Non-Supervisée :", "Pas de règles 'if/else' rigides. L'algorithme isole les observations aberrantes en calculant la profondeur de partitionnement dans une forêt d'arbres décisionnels."),
        ("Entraînement Nominal Préalable :", "Modèle entraîné sur 1 500 échantillons de trafic sain (train_baseline.py) avec un taux de contamination calibré à 3%."),
        ("Légèreté & Performance Temps Réel :", "Zéro dépendance GPU. Inférence instantanée en moins de 5 millisecondes, directement exécutable en mémoire sur le PC Hôte."),
        ("Garde-fous Anti-Faux Positifs :", "Une charge nominale ou un système au repos (sans erreur et latence < 150ms) ne déclenche jamais d'alerte intempestive.")
    ]
    for title, desc in ml_points:
        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_NAVY
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = COLOR_MUTED

    # Right: The 4D Feature Vector
    add_card(s7, 6.8, 1.5, 5.733, 5.5, bg_color=COLOR_DARK_CARD, border_color=COLOR_BLUE)
    b = s7.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.333), Inches(5.1))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Le Vecteur Télémétrique 4D Ingesté"
    p.font.name = FONT_TITLE
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    features = [
        ("1. request_rate (req/s)", "Débit réel calculé par dérivation différentielle entre deux scrapes successifs."),
        ("2. avg_latency_ms (ms)", "Latence moyenne de réponse de l'API de paiement (détecte l'asphyxie et le Slowloris)."),
        ("3. error_rate_5xx (%)", "Ratio d'échecs serveur par rapport au volume global de requêtes."),
        ("4. active_requests (connexions)", "Nombre de connexions HTTP concurrentes en cours de traitement par le serveur.")
    ]
    for feat, f_desc in features:
        p_t = tf.add_paragraph()
        p_t.text = feat
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(11.5)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_ACCENT
        p_d = tf.add_paragraph()
        p_d.text = f_desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = RGBColor(255, 255, 255)

    p_rule = tf.add_paragraph()
    p_rule.text = "\nRègle de Déclenchement de Reprise :"
    p_rule.font.name = FONT_TITLE
    p_rule.font.size = Pt(11.5)
    p_rule.font.bold = True
    p_rule.font.color.rgb = RGBColor(255, 255, 255)
    p_rdesc = tf.add_paragraph()
    p_rdesc.text = "2 anomalies consécutives confirmées (Score < 0) ➔ Émission Webhook immédiate au Moteur de Remédiation."
    p_rdesc.font.name = FONT_BODY
    p_rdesc.font.size = Pt(10.5)
    p_rdesc.font.color.rgb = COLOR_GREEN

    set_notes(s7, """[MACHINE LEARNING AIOPS - 3:15 à 3:45]
Pour la détection d'anomalies, le sujet proscrivait les simples seuils fixes codés en dur.
Nous avons implémenté un modèle non supervisé Isolation Forest avec Scikit-learn.
Toutes les 3 secondes, notre script extrait un vecteur télémétrique à quatre dimensions : le débit de requêtes par seconde, la latence moyenne en millisecondes, le taux d'erreurs 5xx, et les requêtes concurrentes actives.
Le modèle compare ce vecteur à la distribution normale. Dès que deux cycles consécutifs signalent une anomalie comportementale — même sans plantage brutal du conteneur —, le détecteur expédie un webhook vers le moteur de remédiation.""")

    # =========================================================================
    # SLIDE 8 : LA CHAÎNE ZERO-TOUCH RECOVERY EN 5 ÉTAPES
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Le Cœur de la Résilience : La Chaîne Zero-Touch en 5 Étapes")

    # 5 Sequential Cards
    steps = [
        ("T = 0s", "Attaque Red Team", "L'attaquant externe déclenche une attaque Slowloris ou Chaos API qui contourne le WAF.", COLOR_RED),
        ("T + 3s", "Dégradation Métier", "La latence s'envole (> 1000ms) et les erreurs 500 augmentent. Le dashboard passe à l'orange.", COLOR_AMBER),
        ("T + 6s", "Détection AIOps", "L'Isolation Forest confirme l'anomalie sur 2 cycles successifs et émet un webhook d'incident.", COLOR_BLUE),
        ("T + 8s", "Remédiation K8s", "Le moteur ordonne un rollout restart sans coupure des pods ou recrée le conteneur altéré.", COLOR_NAVY),
        ("T + 18s", "Preuve de Reprise", "Le module de validation injecte un paiement réel. Succès 201 Created : voyant vert certifié !", COLOR_GREEN),
    ]

    card_w = 2.22
    gap = 0.15
    for i, (time_tag, step_title, step_desc, color) in enumerate(steps):
        cx = 0.8 + i * (card_w + gap)
        add_card(s8, cx, 1.5, card_w, 4.4, border_color=color, border_width=2)
        
        # Time badge
        badge = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(cx), Inches(1.5), Inches(card_w), Inches(0.7))
        badge.fill.solid()
        badge.fill.fore_color.rgb = color
        badge.line.fill.background()
        tf_b = badge.text_frame
        p = tf_b.paragraphs[0]
        p.text = time_tag
        p.font.name = FONT_TITLE
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.alignment = PP_ALIGN.CENTER

        # Content
        b = s8.shapes.add_textbox(Inches(cx + 0.1), Inches(2.3), Inches(card_w - 0.2), Inches(3.4))
        tf = b.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = step_title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_NAVY

        p_d = tf.add_paragraph()
        p_d.text = "\n" + step_desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = COLOR_NAVY

    # Callout banner at bottom
    add_card(s8, 0.8, 6.05, 11.733, 0.95, bg_color=COLOR_CARD_BG, border_color=COLOR_GREEN, border_width=2)
    b_bot = s8.shapes.add_textbox(Inches(1.0), Inches(6.12), Inches(11.333), Inches(0.8))
    tf_bot = b_bot.text_frame
    tf_bot.word_wrap = True
    p = tf_bot.paragraphs[0]
    p.text = "RÉSULTAT CHIFFRÉ : RTO CONSTATÉ < 20 SECONDES — ZÉRO INTERVENTION HUMAINE REQUISE."
    p.font.name = FONT_TITLE
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN
    p_sub = tf_bot.add_paragraph()
    p_sub.text = "L'ensemble du cycle incident-détection-reprise-validation s'exécute de façon autonome en direct devant le jury."
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(10.5)
    p_sub.font.color.rgb = COLOR_NAVY

    set_notes(s8, """[CYCLE DE VIE DE LA RÉSILIENCE - 3:45 à 4:15]
Voici la chronologie exacte de notre chaîne de cyber-résilience autonome.
En moins de 20 secondes montre en main :
À T0, l'attaque est lancée depuis la machine Red Team.
À T+3s, le service se dégrade, la latence monte.
À T+6s, notre Isolation Forest détecte la signature comportementale anormale et alerte le moteur de remédiation.
À T+8s, le moteur engage l'action corrective sous Kubernetes.
À T+18s, un paiement synthétique est exécuté avec succès.
Le service est pleinement rétabli, sans qu'aucun membre de l'équipe n'ait touché à son clavier.""")

    # =========================================================================
    # SLIDE 9 : MATRICE DES 5 ATTAQUES RED TEAM
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Matrice Red Team vs Blue Team : Les 5 Scénarios Éprouvés")

    # Table of 5 Attacks
    table_shape = s9.shapes.add_table(6, 6, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.4))
    table = table_shape.table

    # Column widths
    table.columns[0].width = Inches(0.8)   # #
    table.columns[1].width = Inches(2.2)   # Attaque
    table.columns[2].width = Inches(2.2)   # Route / Outil
    table.columns[3].width = Inches(2.2)   # Comportement WAF
    table.columns[4].width = Inches(2.5)   # Réaction Cyber-Résilience
    table.columns[5].width = Inches(1.833) # Preuve Jury

    headers = ["#", "Type d'Attaque", "Vecteur & Route", "Action WAF Nginx", "Réaction Résilience", "Preuve Soutenance"]
    for col_idx, h in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_TITLE
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.alignment = PP_ALIGN.CENTER

    rows_data = [
        ("1", "Scan OWASP Top 10", "CLI: mode scanner\nUA: sqlmap / nikto", "BLOQUÉ NET\n(HTTP 403 Forbidden)", "Backend non sollicité,\naucun impact", "Logs WAF 403\nen direct"),
        ("2", "HTTP Flood Volumique", "Next.js / CLI flood\nPOST /api/v1/payments", "RATE-LIMITÉ\n(HTTP 429 Too Many Req)", "Si persistant : scale HPA\nde 3 à 8 réplicas K8s", "Compteur 429 &\nélast. pods"),
        ("3", "Slowloris (Sockets)", "CLI: mode slowloris\nSockets TCP incomplets", "PASSE LE WAF\n(faille réaliste démo)", "Saturation descripteurs ➔\nML AIOps détecte latence ➔ Restart", "Rollout restart\nZero-Touch"),
        ("4", "Chaos & Dégradation", "Next.js / CLI chaos\nPOST /chaos/configure", "PASSE LE WAF\n(payload JSON valide)", "65% erreurs 500 & latence ➔\nIsolation Forest alerte ➔ Restart", "Alerte ML &\ntransaction"),
        ("5", "Crash Fatal Pod", "Next.js: Crash Fatal\nPOST /chaos/crash", "PASSE LE WAF\n(requête interne)", "Sortie conteneur (exit 1) ➔\nSonde K8s recrée le pod", "Self-healing K8s\nen live")
    ]

    for row_idx, data in enumerate(rows_data):
        for col_idx, val in enumerate(data):
            cell = table.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_CARD_BG if row_idx % 2 == 0 else COLOR_CARD_SOFT
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_BODY
            p.font.size = Pt(9)
            p.font.color.rgb = COLOR_NAVY
            if col_idx in [0, 3, 5]:
                p.alignment = PP_ALIGN.CENTER

    set_notes(s9, """[MATRICE D'ATTAQUE - 4:15 à 4:45]
Nous avons préparé 5 attaques distinctes pour tester tous les étages de notre défense.
Les attaques 1 et 2 démontrent l'efficacité de la prévention WAF et du dimensionnement d'infrastructure avec le HPA.
Les attaques 3, 4 et 5 démontrent la cyber-résilience autonome face à l'inévitable :
Que l'incident provienne d'une saturation de descripteurs de sockets (Slowloris), d'un bug applicatif dégradant insidieusement les paiements (Chaos), ou d'un crash fatal physique, notre système dispose de la réponse automatisée adaptée.""")

    # =========================================================================
    # SLIDE 10 : LE CLIP CHRONO (60 SECONDES SANS COUPE)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Le Clip Chrono : 60 Secondes en Continu sans Coupe")

    # 4 Timeline Blocks
    clip_steps = [
        ("00:00 - 00:12", "État Nominal Initial", [
            "Terminal bancaire actif",
            "Transactions clients réussies",
            "Dashboard SOC au vert",
            "Latence nominale ~ 25 ms"
        ], COLOR_GREEN),
        ("00:12 - 00:28", "Déclenchement Attaque", [
            "Lancement depuis PC Attaquant",
            "Trafic hostile injecté",
            "Passage dashboard à l'orange",
            "Explosion de la latence"
        ], COLOR_RED),
        ("00:28 - 00:46", "Détection & Auto-Guérison", [
            "Alerte Machine Learning AIOps",
            "Webhook vers moteur de reprise",
            "K8s redémarre les pods altérés",
            "Zéro action humaine à l'écran"
        ], COLOR_BLUE),
        ("00:46 - 01:00", "Preuve par Transaction", [
            "Service paiement de retour",
            "Nouvelle transaction validée",
            "Voyant vert et certification",
            "Service opérationnel !"
        ], COLOR_NAVY)
    ]

    card_w = 2.8
    gap = 0.17
    for i, (timing, title, bullets, color) in enumerate(clip_steps):
        cx = 0.8 + i * (card_w + gap)
        add_card(s10, cx, 1.5, card_w, 4.4, border_color=color, border_width=2)
        
        # Header banner
        banner = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(cx), Inches(1.5), Inches(card_w), Inches(0.75))
        banner.fill.solid()
        banner.fill.fore_color.rgb = color
        banner.line.fill.background()
        tf = banner.text_frame
        p = tf.paragraphs[0]
        p.text = timing
        p.font.name = FONT_TITLE
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.alignment = PP_ALIGN.CENTER

        # Title & points
        b = s10.shapes.add_textbox(Inches(cx + 0.1), Inches(2.35), Inches(card_w - 0.2), Inches(3.4))
        tf = b.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_NAVY

        for pt in bullets:
            p_p = tf.add_paragraph()
            p_p.text = "• " + pt
            p_p.font.name = FONT_BODY
            p_p.font.size = Pt(10)
            p_p.font.color.rgb = COLOR_NAVY

    # Bottom Requirements check
    add_card(s10, 0.8, 6.05, 11.733, 0.95, bg_color=COLOR_DARK_CARD, border_color=COLOR_ACCENT)
    b = s10.shapes.add_textbox(Inches(1.0), Inches(6.12), Inches(11.333), Inches(0.8))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "CONFORMITÉ NATIONALE DU CLIP CHRONO (15 POINTS NATIONAUX / 4 POINTS LOCAUX) :"
    p.font.name = FONT_TITLE
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    p2 = tf.add_paragraph()
    p2.text = "Format MP4 strict, exactement 60 secondes, capture continue sans coupe, horodatage visible, bande sonore explicative et titrage clair."
    p2.font.name = FONT_BODY
    p2.font.size = Pt(10.5)
    p2.font.color.rgb = RGBColor(255, 255, 255)

    set_notes(s10, """[CLIP CHRONO 60 SECONDES - 4:45 à 5:15]
Le Clip Chrono est un livrable capital évalué sur 15 points en finale nationale.
Notre vidéo respecte scrupuleusement les exigences du cahier des charges :
Exactement 60 secondes, filmée en continu sans aucune coupe.
On y observe successivement l'état nominal, le déclenchement de l'attaque depuis la machine Red Team, la prise en charge immédiate par notre détecteur AIOps, le travail silencieux du moteur de remédiation, et enfin la réactivation immédiate attestée par un paiement validé.""")

    # =========================================================================
    # SLIDE 11 : PILIER GOUVERNANCE — EBIOS RISK MANAGER
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "Pilier GOUVERNANCE : Démarche d'Analyse de Risques EBIOS RM")

    # 5 Workshops EBIOS RM in cards
    ebios_steps = [
        ("Atelier 1", "Cadrage & Socle", [
            "Valeurs métiers : Traitement continu des paiements bancaires.",
            "Biens supports : Pods FastAPI, base Postgres, Ingress WAF.",
            "Événements redoutés : Perte de disponibilité > 1 min, altération de transactions."
        ]),
        ("Atelier 2", "Sources de Risques", [
            "Cybercriminels motivés par l'extorsion et la rançon.",
            "Concurrents déloyaux visant la déstabilisation d'image.",
            "Hacktivistes ciblant les infrastructures financières critiques."
        ]),
        ("Atelier 3", "Scénarios Stratégiques", [
            "DDoS volumétrique sur l'API publique.",
            "Asphyxie insidieuse des ressources serveur (Slowloris).",
            "Compromission de secrets d'administration SOC."
        ]),
        ("Atelier 4", "Scénarios Opérationnels", [
            "Saturation des descripteurs de fichiers TCP.",
            "Injection d'erreurs 500 par corruption de payload JSON.",
            "Tentatives d'exfiltration via requêtes forgées."
        ]),
        ("Atelier 5", "Traitement du Risque", [
            "Prévention : Durcissement WAF L7 & Rate Limiting.",
            "Résilience : Détection AIOps & Reprise Zero-Touch K8s.",
            "Risque résiduel maîtrisé et accepté par la direction."
        ])
    ]

    col_w = 2.22
    col_gap = 0.15
    for i, (title, subtitle, points) in enumerate(ebios_steps):
        cx = 0.8 + i * (col_w + col_gap)
        add_card(s11, cx, 1.5, col_w, 5.5)
        
        # Header box
        h_box = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(cx), Inches(1.5), Inches(col_w), Inches(0.8))
        h_box.fill.solid()
        h_box.fill.fore_color.rgb = COLOR_NAVY
        h_box.line.fill.background()
        tf = h_box.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.alignment = PP_ALIGN.CENTER
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.name = FONT_BODY
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = COLOR_ACCENT
        p2.alignment = PP_ALIGN.CENTER

        # Bullets
        b = s11.shapes.add_textbox(Inches(cx + 0.1), Inches(2.4), Inches(col_w - 0.2), Inches(4.4))
        tf = b.text_frame
        tf.word_wrap = True
        for pt_idx, pt in enumerate(points):
            p = tf.paragraphs[0] if pt_idx == 0 else tf.add_paragraph()
            p.text = "• " + pt
            p.font.name = FONT_BODY
            p.font.size = Pt(9.5)
            p.font.color.rgb = COLOR_NAVY

    set_notes(s11, """[GOUVERNANCE EBIOS RM - 5:15 à 5:45]
La résilience technique ne vaut que si elle sert les priorités stratégiques de l'entreprise.
Nous avons structuré notre gestion des risques selon la méthodologie de référence de l'ANSSI : EBIOS Risk Manager, articulée en cinq ateliers.
Nous avons identifié les événements redoutés majeurs : l'arrêt des encaissements et la perte de traçabilité bancaire.
Notre démonstrateur technique concrétise directement le traitement des risques de l'Atelier 5 : le risque d'indisponibilité prolongée est neutralisé par le couplage WAF et remédiation autonome Zero-Touch.""")

    # =========================================================================
    # SLIDE 12 : CONFORMITÉ DORA & DIRECTIVE NIS2
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "Gouvernance : Alignement Règlement DORA & Directive NIS2")

    # 2 Big Cards
    add_card(s12, 0.8, 1.5, 5.7, 5.5)
    b = s12.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(5.1))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Règlement DORA (Secteur Financier UE)"
    p.font.name = FONT_TITLE
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    dora_pts = [
        ("Article 6 — Gestion du risque TIC :", "Obligation de concevoir des systèmes tolérants aux pannes avec redondance active (3 réplicas API + HPA)."),
        ("Article 17 — Notification des incidents majeurs :", "Collecte télémétrique temps réel, détection instantanée et génération de logs auditables Loki."),
        ("Article 24 — Tests de résilience opérationnelle :", "Campagnes régulières d'attaques Red Team et de Chaos Engineering automatisées."),
        ("Article 28 — Gestion des risques liés aux tiers :", "Filtrage et étanchéité stricts des flux API d'interconnexion bancaire via WAF L7.")
    ]
    for title, desc in dora_pts:
        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_NAVY
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = COLOR_MUTED

    add_card(s12, 6.8, 1.5, 5.733, 5.5, bg_color=COLOR_CARD_SOFT)
    b = s12.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.333), Inches(5.1))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Directive NIS2 & Hygiène ANSSI"
    p.font.name = FONT_TITLE
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    nis2_pts = [
        ("Entités Essentielles / Importantes :", "Les opérateurs de paiement relèvent des critères de haute criticité de la directive européenne NIS2."),
        ("Délais de Déclaration Stricts :", "Obligation de signalement d'un incident significatif à l'ANSSI sous 24 heures (alerte précoce) et 72 heures (rapport détaillé)."),
        ("Cloisonnement & Moindre Privilège :", "Mise en œuvre du principe Zero-Trust : jetons JWT pour l'administration SOC, ports internes isolés à 127.0.0.1."),
        ("Responsabilité de la Gouvernance :", "La direction doit approuver et auditer régulièrement le PCA/PRA et les résultats de cyber-résilience.")
    ]
    for title, desc in nis2_pts:
        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_NAVY
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = COLOR_NAVY

    set_notes(s12, """[RÉGLEMENTATION DORA & NIS2 - 5:45 à 6:15]
Notre architecture s'inscrit en totale conformité avec les réglementations européennes majeures.
DORA, en vigueur depuis 2025, impose aux institutions financières des obligations précises de résilience opérationnelle numérique : notre système répond directement à l'article 6 sur la redondance et à l'article 24 sur les tests d'intrusion.
NIS2 renforce la responsabilité des organes de gouvernance et impose la traçabilité intégrale des incidents : notre stack Loki/Prometheus garantit l'auditabilité exigée en cas d'enquête post-incident.""")

    # =========================================================================
    # SLIDE 13 : STRATÉGIE PCA / PRA & RECOMMANDATIONS
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "PCA / PRA Métier & Recommandations Stratégiques")

    # Left: KPIs PCA / PRA
    add_card(s13, 0.8, 1.5, 5.7, 5.5, bg_color=COLOR_DARK_CARD, border_color=COLOR_ACCENT)
    b = s13.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(5.1))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Métriques Cibles du PCA / PRA"
    p.font.name = FONT_TITLE
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    pca_kpis = [
        ("RTO Constaté (Temps de Reprise) :", "< 20 secondes", "Alors que les interventions manuelles prennent entre 15 et 45 minutes, le Zero-Touch divise le temps d'arrêt par 50."),
        ("RPO Constaté (Perte de Données) :", "= 0 seconde", "Grâce à l'idempotence des transactions et à la persistance PostgreSQL transactionnelle ACID."),
        ("Disponibilité Cible Démontrée :", "99.95 %", "Haute disponibilité assurée par le multi-pods et l'auto-scaling HPA sous Kubernetes.")
    ]
    for title, val, desc in pca_kpis:
        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_ACCENT
        p_v = tf.add_paragraph()
        p_v.text = val
        p_v.font.name = FONT_TITLE
        p_v.font.size = Pt(16)
        p_v.font.bold = True
        p_v.font.color.rgb = COLOR_GREEN
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = RGBColor(255, 255, 255)

    # Right: Recommendations to Executive Committee
    add_card(s13, 6.8, 1.5, 5.733, 5.5)
    b = s13.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.333), Inches(5.1))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Recommandations à la Direction Générale"
    p.font.name = FONT_TITLE
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    recs = [
        ("1. Industrialiser l'AIOps en Production :", "Étendre le modèle Isolation Forest à l'ensemble des passerelles bancaires et microservices de facturation."),
        ("2. Déployer une Architecture Multi-Régions :", "Répliquer les clusters Kubernetes sur deux zones de disponibilité distinctes pour résister à une panne physique de datacenter."),
        ("3. Intégrer le Chaos Engineering en CI/CD :", "Injecter automatiquement des pannes contrôlées à chaque release pour éprouver la non-régression de l'auto-guérison."),
        ("4. Gestionnaire de Secrets d'Entreprise :", "Migrer vers HashiCorp Vault pour la rotation dynamique des certificats et des secrets applicatifs.")
    ]
    for title, desc in recs:
        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_NAVY
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = COLOR_MUTED

    set_notes(s13, """[PCA/PRA & RECOMMANDATIONS STRATÉGIQUES - 6:15 à 6:45]
Sur le plan du Plan de Continuité et de Reprise d'Activité, les chiffres parlent d'eux-mêmes :
Notre RTO passe de plus de 30 minutes en manuel à moins de 20 secondes en automatique.
Notre RPO est nul : aucune transaction bancaire n'est perdue.
Si nous devions transposer ce prototype dans un grand établissement financier, nous recommanderions à la direction trois axes majeurs : le déploiement multi-régions actif-actif, l'intégration du Chaos Engineering au cœur du pipeline CI/CD, et la généralisation du modèle AIOps.""")

    # =========================================================================
    # SLIDE 14 : BILAN DU CONSORTIUM & RÉPARTITION
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)
    add_header(s14, "Bilan du Sprint : Synergie d'Équipe & Maîtrise Technique")

    # 5 Team member contribution cards
    members_data = [
        ("Théo", "Architecture & K8s", [
            "Conception Helm Chart & manifests K8s.",
            "Configuration Kind, Ingress & HPA.",
            "Automatisation Ansible & déploiement.",
            "Orchestration et tests de charge."
        ]),
        ("Mael", "Développement Métier", [
            "Développement FastAPI Payment API.",
            "Modélisation PostgreSQL & idempotence.",
            "Microservice Auth JWT Bearer.",
            "Frontend React/Tailwind & API Docs."
        ]),
        ("Flora", "Cybersécurité & WAF", [
            "Configuration durcie Nginx WAF L7.",
            "Règles anti-scanners & rate limiting.",
            "Développement console Red Team.",
            "Audit sécurité & brèche WAF bypass."
        ]),
        ("Fely", "IA / DATA & AIOps", [
            "Algorithme ML Isolation Forest.",
            "Génération baseline & entraînement.",
            "Boucle temps réel & connecteur webhook.",
            "Assistant local RAG Ollama / LangChain."
        ]),
        ("Aymeric", "Gouvernance & Risques", [
            "Analyse structurée EBIOS RM (5 ateliers).",
            "Dossier de conformité DORA & NIS2.",
            "Élaboration du PCA / PRA et RTO/RPO.",
            "Recommandations de pilotage stratégique."
        ])
    ]

    col_w = 2.22
    col_gap = 0.15
    for i, (name, role, tasks) in enumerate(members_data):
        cx = 0.8 + i * (col_w + col_gap)
        add_card(s14, cx, 1.5, col_w, 4.4, border_color=COLOR_ACCENT)
        
        # Header banner
        banner = s14.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(cx), Inches(1.5), Inches(col_w), Inches(0.75))
        banner.fill.solid()
        banner.fill.fore_color.rgb = COLOR_NAVY
        banner.line.fill.background()
        tf = banner.text_frame
        p = tf.paragraphs[0]
        p.text = name
        p.font.name = FONT_TITLE
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.alignment = PP_ALIGN.CENTER
        p2 = tf.add_paragraph()
        p2.text = role
        p2.font.name = FONT_BODY
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = COLOR_ACCENT
        p2.alignment = PP_ALIGN.CENTER

        # Tasks
        b = s14.shapes.add_textbox(Inches(cx + 0.1), Inches(2.35), Inches(col_w - 0.2), Inches(3.4))
        tf = b.text_frame
        tf.word_wrap = True
        for t_idx, t in enumerate(tasks):
            p = tf.paragraphs[0] if t_idx == 0 else tf.add_paragraph()
            p.text = "✓ " + t
            p.font.name = FONT_BODY
            p.font.size = Pt(9.5)
            p.font.color.rgb = COLOR_NAVY

    # Bottom IA mastery mention
    add_card(s14, 0.8, 6.05, 11.733, 0.95, bg_color=COLOR_DARK_CARD, border_color=COLOR_ACCENT)
    b = s14.shapes.add_textbox(Inches(1.0), Inches(6.12), Inches(11.333), Inches(0.8))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "MAÎTRISE COMPLÈTE DU CODE & USAGE DE L'IA GÉNÉRATIVE :"
    p.font.name = FONT_TITLE
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    p2 = tf.add_paragraph()
    p2.text = "Conformément à la grille d'évaluation Axe 5, 100% du code produit et généré avec assistance IA a été revu, durci, testé par tests unitaires (pytest) et validé en conditions réelles."
    p2.font.name = FONT_BODY
    p2.font.size = Pt(10.5)
    p2.font.color.rgb = RGBColor(255, 255, 255)

    set_notes(s14, """[ENGAGEMENT DU CONSORTIUM - 6:45 à 7:15]
Ce projet a été réalisé en mode commando au fil d'un sprint intensif de quatre jours.
Chaque membre du consortium a pris en charge un domaine d'expertise précis, tout en conservant une vision transverse de bout en bout.
Concernant l'utilisation des outils d'IA générative autorisés dans le sujet : nous avons exercé une relecture et un durcissement critiques sur chaque fichier. L'intégralité des microservices et des scripts est couverte par notre suite de tests automatisés pytest.""")

    # =========================================================================
    # SLIDE 15 : DÉMONSTRATION EN DIRECT & QUESTIONS / RÉPONSES
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15, COLOR_NAVY)

    add_card(s15, 0.8, 0.8, 11.733, 5.9, bg_color=COLOR_NAVY, border_color=COLOR_ACCENT, border_width=2)

    # Title box
    tb = s15.shapes.add_textbox(Inches(1.3), Inches(1.3), Inches(10.7), Inches(1.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "DÉMONSTRATION EN DIRECT"
    p.font.name = FONT_TITLE
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    p2 = tf.add_paragraph()
    p2.text = "Passage à la Démonstration Live (3 min) & Session d'Échanges avec le Jury"
    p2.font.name = FONT_BODY
    p2.font.size = Pt(16)
    p2.font.color.rgb = COLOR_BG

    # 3 Access Cards
    access_points = [
        ("Terminal Bancaire Client", "http://localhost:3000", "Accès public non filtré simulant les achats en ligne des utilisateurs finaux."),
        ("Console Supervision SOC", "http://localhost:3000/supervision", "Accès sécurisé JWT Bearer : métriques AIOps, statut réplicas et logs."),
        ("Console Attaquant Red Team", "http://localhost:3001", "Module externe autonome sur PC distinct : déclenchement des attaques.")
    ]
    card_w = 3.4
    gap = 0.25
    for i, (title, url, desc) in enumerate(access_points):
        cx = 1.3 + i * (card_w + gap)
        add_card(s15, cx, 3.0, card_w, 2.0, bg_color=RGBColor(48, 40, 88), border_color=COLOR_ACCENT)
        b = s15.shapes.add_textbox(Inches(cx + 0.15), Inches(3.15), Inches(card_w - 0.3), Inches(1.7))
        tf = b.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = RGBColor(255, 255, 255)

        p_u = tf.add_paragraph()
        p_u.text = url
        p_u.font.name = FONT_TITLE
        p_u.font.size = Pt(11)
        p_u.font.bold = True
        p_u.font.color.rgb = COLOR_GREEN

        p_d = tf.add_paragraph()
        p_d.text = "\n" + desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = COLOR_BG

    # Bottom final quote
    b_bot = s15.shapes.add_textbox(Inches(1.3), Inches(5.3), Inches(10.7), Inches(1.1))
    tf = b_bot.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "« PROJECT RESILIENCE-ALPHA : La cyber-résilience ne se promet pas, elle se démontre. »"
    p.font.name = FONT_BODY
    p.font.size = Pt(14)
    p.font.italic = True
    p.font.color.rgb = COLOR_ACCENT
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = "Merci pour votre attention. Nous lançons à présent le scénario d'attaque en direct !"
    p2.font.name = FONT_TITLE
    p2.font.size = Pt(15)
    p2.font.bold = True
    p2.font.color.rgb = RGBColor(255, 255, 255)
    p2.alignment = PP_ALIGN.CENTER

    set_notes(s15, """[TRANSITION DÉMO LIVE & QUESTIONS JURY]
Nous vous remercions pour votre écoute.
Nous passons immédiatement à la démonstration en direct sur nos postes :
1. Sur le PC Hôte, nous observons le terminal de paiement et le tableau de bord de supervision SOC.
2. Depuis le PC Attaquant distinct, nous déclenchons l'attaque en direct.
3. Observez la détection instantanée de l'Isolation Forest et la reprise autonome par le moteur de remédiation, certifiée par l'émission réussie d'une transaction.
Nous sommes à votre disposition pour répondre à toutes vos questions.""")

    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path}")

if __name__ == "__main__":
    out_dir = r"c:\Users\buzz_\Bureau\code\Workshop"
    out_file = os.path.join(out_dir, "Workshop2026-M2-G1-Pres.pptx")
    create_deck(out_file)
    # Also save a copy inside Code/
    code_out_file = os.path.join(out_dir, "Code", "Workshop2026-M2-G1-Pres.pptx")
    create_deck(code_out_file)
