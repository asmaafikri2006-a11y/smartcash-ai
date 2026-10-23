"""
SmartCash AI - Application de Prévision de Trésorerie à Court Terme
Développée en Python & Streamlit pour les étudiants et gestionnaires en Gestion Financière et Comptable.
Devise : Dirham marocain (DH).
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os

from data_generator import charger_ou_generer_donnees
from ml_model import ModelePrevisionTresorerie

# ==========================================
# Configuration de la page Streamlit
# ==========================================
st.set_page_config(
    page_title="SmartCash AI | Prévision de Trésorerie",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# Style CSS personnalisé & Finitions Pro
# ==========================================
st.markdown("""
<style>
    /* Polices et conteneurs généraux */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0369a1 100%);
        padding: 24px 28px;
        border-radius: 16px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15);
    }
    
    .main-header h1 {
        color: #ffffff !important;
        font-weight: 800;
        font-size: 2.1rem;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        color: #e2e8f0;
        font-size: 1.05rem;
        margin-bottom: 0;
    }
    
    .badge-maroc {
        background: rgba(255, 255, 255, 0.15);
        color: #38bdf8;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        margin-top: 10px;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    
    /* Cartes de statistiques / KPIs */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
    }
    
    .metric-title {
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 6px;
    }
    
    .metric-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0f172a;
    }
    
    /* Alertes de trésorerie */
    .alert-box {
        padding: 20px 24px;
        border-radius: 14px;
        margin: 20px 0;
        font-weight: 500;
    }
    
    .alert-green {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border-left: 6px solid #10b981;
        color: #065f46;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.12);
    }
    
    .alert-orange {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border-left: 6px solid #f59e0b;
        color: #92400e;
        box-shadow: 0 4px 14px rgba(245, 158, 11, 0.12);
    }
    
    .alert-red {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border-left: 6px solid #ef4444;
        color: #991b1b;
        box-shadow: 0 4px 14px rgba(239, 68, 68, 0.15);
    }
    
    .alert-title {
        font-size: 1.25rem;
        font-weight: 800;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .pedago-card {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 15px;
    }
    
    .stNumberInput label {
        font-weight: 600 !important;
        color: #1e293b !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# Fonctions Utilitaires de Formatage
# ==========================================
def format_dh(valeur):
    """Formate un nombre en Dirhams marocains avec séparateur d'espaces."""
    return f"{valeur:,.2f} DH".replace(",", " ").replace(".", ",")

# ==========================================
# Chargement des Données & Modèle ML
# ==========================================
@st.cache_data
def charger_donnees():
    return charger_ou_generer_donnees()

df_historique = charger_donnees()

@st.cache_resource
def entrainer_modele(df):
    modele = ModelePrevisionTresorerie()
    metrics = modele.entrainer(df)
    return modele, metrics

modele_ml, metrics_ml = entrainer_modele(df_historique)

# Dernier mois de l'historique
dernier_solde_reel = float(df_historique["Solde_Final_DH"].iloc[-1])
prevision_prochain_mois = modele_ml.prevoir_mois_suivants(nb_mois=1, solde_initial_depart=dernier_solde_reel).iloc[0]

# ==========================================
# Barre Latérale (Paramètres & Scénarios)
# ==========================================
st.sidebar.image("https://img.icons8.com/fluency/96/money-circulation.png", width=70)
st.sidebar.title("SmartCash AI")
st.sidebar.caption("Système d'Aide à la Décision Financière")
st.sidebar.markdown("---")

st.sidebar.subheader("🎯 Scénarios Prédéfinis")
st.sidebar.write("Testez en un clic les 3 situations types :")

col_sc1, col_sc2 = st.sidebar.columns(2)
col_sc3, col_sc4 = st.sidebar.columns(2)

# Initialisation des états de session si absents
if "solde_init" not in st.session_state:
    st.session_state.solde_init = float(dernier_solde_reel)
if "reglements_clients" not in st.session_state:
    st.session_state.reglements_clients = float(prevision_prochain_mois["Total_Encaissements_Prevu_DH"] * 0.90)
if "autres_encaissements" not in st.session_state:
    st.session_state.autres_encaissements = float(prevision_prochain_mois["Total_Encaissements_Prevu_DH"] * 0.10)
if "fournisseurs" not in st.session_state:
    st.session_state.fournisseurs = float(prevision_prochain_mois["Total_Decaissements_Prevu_DH"] * 0.52)
if "salaires" not in st.session_state:
    st.session_state.salaires = 42000.0
if "loyer" not in st.session_state:
    st.session_state.loyer = 12000.0
if "autres_charges" not in st.session_state:
    st.session_state.autres_charges = 8500.0

if col_sc1.button("🟢 Confort", help="Situation très favorable avec excédent"):
    st.session_state.solde_init = 120000.0
    st.session_state.reglements_clients = 190000.0
    st.session_state.autres_encaissements = 15000.0
    st.session_state.fournisseurs = 65000.0
    st.session_state.salaires = 40000.0
    st.session_state.loyer = 12000.0
    st.session_state.autres_charges = 8000.0
    st.rerun()

if col_sc2.button("🟠 Tendu", help="Trésorerie positive mais inférieure au seuil de sécurité"):
    st.session_state.solde_init = 18000.0
    st.session_state.reglements_clients = 125000.0
    st.session_state.autres_encaissements = 0.0
    st.session_state.fournisseurs = 78000.0
    st.session_state.salaires = 42000.0
    st.session_state.loyer = 12000.0
    st.session_state.autres_charges = 6000.0
    st.rerun()

if col_sc3.button("🔴 Critique", help="Déficit de trésorerie / risque de découvert bancaire"):
    st.session_state.solde_init = 5000.0
    st.session_state.reglements_clients = 70000.0
    st.session_state.autres_encaissements = 0.0
    st.session_state.fournisseurs = 85000.0
    st.session_state.salaires = 45000.0
    st.session_state.loyer = 12000.0
    st.session_state.autres_charges = 12000.0
    st.rerun()

if col_sc4.button("🤖 Prévision IA", help="Applique les prévisions générées par le Machine Learning"):
    st.session_state.solde_init = float(dernier_solde_reel)
    st.session_state.reglements_clients = float(prevision_prochain_mois["Total_Encaissements_Prevu_DH"] * 0.90)
    st.session_state.autres_encaissements = float(prevision_prochain_mois["Total_Encaissements_Prevu_DH"] * 0.10)
    st.session_state.fournisseurs = float(prevision_prochain_mois["Total_Decaissements_Prevu_DH"] * 0.52)
    st.session_state.salaires = 42000.0
    st.session_state.loyer = 12000.0
    st.session_state.autres_charges = float(prevision_prochain_mois["Total_Decaissements_Prevu_DH"] - (prevision_prochain_mois["Total_Decaissements_Prevu_DH"] * 0.52) - 42000 - 12000)
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Paramètres Financiers")
seuil_securite = st.sidebar.number_input(
    "Seuil de sécurité minimum (DH) :",
    min_value=0.0,
    max_value=200000.0,
    value=25000.0,
    step=5000.0,
    help="Montant de sécurité en dessous duquel la trésorerie est jugée tendue."
)

st.sidebar.info("""
**À propos :**
SmartCash AI est un simulateur pédagogique destiné aux étudiants et gestionnaires en Finance d'Entreprise au Maroc.
""")

# ==========================================
# En-tête Principal
# ==========================================
st.markdown("""
<div class="main-header">
    <h1>SmartCash AI — Prévision de Trésorerie à Court Terme</h1>
    <p>Outil d'analyse prévisionnelle et d'aide à la décision financière pour PME marocaines</p>
    <div class="badge-maroc">🇲🇦 Devise : Dirham Marocain (DH) &nbsp;|&nbsp; 📊 Modélisation Machine Learning intégrée</div>
</div>
""", unsafe_allow_html=True)

# Onglets principaux
tab_budget, tab_ml, tab_historique, tab_guide = st.tabs([
    "💰 Budget de Trésorerie & Diagnostic",
    "🤖 Prévisions Machine Learning",
    "📈 Données Historiques (24 mois)",
    "📚 Guide de l'Étudiant (Gestion & Comptabilité)"
])

# ==========================================
# ONGLET 1 : BUDGET DU MOIS & DIAGNOSTIC
# ==========================================
with tab_budget:
    st.subheader("1. Saisie des Prévisions de Trésorerie du Mois")
    st.caption("Renseignez les données estimées ci-dessous pour calculer le solde final et analyser la situation.")

    # Formulaire de saisie sur 3 colonnes
    col_init, col_enc, col_dec = st.columns([1, 1.2, 1.2])

    with col_init:
        st.markdown("##### 🏦 1. Trésorerie de Départ")
        solde_initial = st.number_input(
            "Solde Initial en Banque & Caisse (DH) :",
            value=float(st.session_state.solde_init),
            step=5000.0,
            key="input_solde_init",
            help="Argent disponible au 1er jour du mois (comptes bancaires + caisse)."
        )
        st.write("")
        st.metric(label="Solde Initial Saisi", value=format_dh(solde_initial))

    with col_enc:
        st.markdown("##### 📥 2. Encaissements Prévus (Entrées)")
        reglements_clients = st.number_input(
            "Règlements Clients attendus (DH) :",
            value=float(st.session_state.reglements_clients),
            min_value=0.0,
            step=5000.0,
            key="input_reglements_clients",
            help="Paiements clients prévus au cours du mois (virements, chèques, effets échus)."
        )
        autres_encaissements = st.number_input(
            "Autres Encaissements (DH) :",
            value=float(st.session_state.autres_encaissements),
            min_value=0.0,
            step=2000.0,
            key="input_autres_encaissements",
            help="Remboursements TVA, subventions, apports en compte courant, etc."
        )
        total_encaissements = reglements_clients + autres_encaissements
        st.metric(label="Total des Encaissements", value=format_dh(total_encaissements))

    with col_dec:
        st.markdown("##### 📤 3. Décaissements Prévus (Sorties)")
        fournisseurs = st.number_input(
            "Paiements Fournisseurs (DH) :",
            value=float(st.session_state.fournisseurs),
            min_value=0.0,
            step=5000.0,
            key="input_fournisseurs",
            help="Règlements des factures d'achats de matières ou marchandises."
        )
        salaires = st.number_input(
            "Salaires & Charges Sociales (DH) :",
            value=float(st.session_state.salaires),
            min_value=0.0,
            step=2000.0,
            key="input_salaires",
            help="Masse salariale nette + cotisations CNSS / AMO."
        )
        loyer = st.number_input(
            "Loyer & Charges Fixes (DH) :",
            value=float(st.session_state.loyer),
            min_value=0.0,
            step=1000.0,
            key="input_loyer",
            help="Loyer des locaux professionnels, eau, électricité, internet."
        )
        autres_charges = st.number_input(
            "Autres Décaissements (DH) :",
            value=float(st.session_state.autres_charges),
            min_value=0.0,
            step=1000.0,
            key="input_autres_charges",
            help="Impôts & taxes, mensualités d'emprunt, carburant, frais divers."
        )
        total_decaissements = fournisseurs + salaires + loyer + autres_charges
        st.metric(label="Total des Décaissements", value=format_dh(total_decaissements))

    # ==========================================
    # Calcul de Trésorerie
    # ==========================================
    # Formule demandée : Solde initial + Encaissements - Décaissements
    flux_net = total_encaissements - total_decaissements
    solde_previsionnel = solde_initial + total_encaissements - total_decaissements

    st.markdown("---")
    st.subheader("2. Résultats & Indicateurs Clés")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric(
            label="Trésorerie Initiale",
            value=format_dh(solde_initial)
        )
    with kpi2:
        st.metric(
            label="Total Encaissements",
            value=f"+ {format_dh(total_encaissements)}",
            delta=f"+{round((total_encaissements/(solde_initial if solde_initial != 0 else 1))*100, 1)}% vs solde init"
        )
    with kpi3:
        st.metric(
            label="Total Décaissements",
            value=f"- {format_dh(total_decaissements)}",
            delta=f"-{round((total_decaissements/(total_encaissements if total_encaissements != 0 else 1))*100, 1)}% du CA encaissé",
            delta_color="inverse"
        )
    with kpi4:
        delta_str = f"+ {format_dh(flux_net)}" if flux_net >= 0 else f"- {format_dh(abs(flux_net))}"
        st.metric(
            label="Solde Prévisionnel Final",
            value=format_dh(solde_previsionnel),
            delta=delta_str,
            delta_color="normal" if flux_net >= 0 else "inverse"
        )

    # ==========================================
    # Système d'Alertes Tricolore
    # ==========================================
    st.markdown("---")
    st.subheader("3. Diagnostic et Système d'Alerte")

    # Ratio de couverture des décaissements en jours
    decaissement_journalier = total_decaissements / 30 if total_decaissements > 0 else 1
    jours_couverture = max(0.0, round(solde_previsionnel / decaissement_journalier, 1))

    if solde_previsionnel > seuil_securite:
        # ALERTE VERTE
        st.markdown(f"""
        <div class="alert-box alert-green">
            <div class="alert-title">🟢 SITUATION SAINE — Excédent de Trésorerie Confortable</div>
            <p><strong>Solde Prévisionnel : {format_dh(solde_previsionnel)}</strong> (supérieur au seuil de sécurité de {format_dh(seuil_securite)}).</p>
            <p><strong>Autonomie financière :</strong> Le solde prévisionnel assure environ <strong>{jours_couverture} jours</strong> de couverture des décaissements mensuels.</p>
            <hr style="border: 0; border-top: 1px solid rgba(16, 185, 129, 0.3); margin: 12px 0;">
            <p><strong>💡 Recommandations financières :</strong></p>
            <ul>
                <li><strong>Placement des excédents :</strong> Envisagez de placer les liquidités dormantes sur des supports à court terme sécurisés (Dépôts à terme - DAT ou OPCVM Monétaires) pour générer des produits financiers.</li>
                <li><strong>Escomptes de règlement :</strong> Négociez avec vos fournisseurs clés un escompte de caisse (ex: 1% à 2%) en contrepartie d'un paiement anticipé.</li>
                <li><strong>Investissements d'exploitation :</strong> Vous disposez de la marge nécessaire pour autofinancer de petits investissements productifs.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    elif 0 <= solde_previsionnel <= seuil_securite:
        # ALERTE ORANGE
        st.markdown(f"""
        <div class="alert-box alert-orange">
            <div class="alert-title">🟠 SITUATION TENDUE — Trésorerie Positive mais Risque Élevé</div>
            <p><strong>Solde Prévisionnel : {format_dh(solde_previsionnel)}</strong> (inférieur au seuil de sécurité recommandé de {format_dh(seuil_securite)}).</p>
            <p><strong>Autonomie financière :</strong> Votre marge de sécurité ne représente que <strong>{jours_couverture} jours</strong> de dépenses.</p>
            <hr style="border: 0; border-top: 1px solid rgba(245, 158, 11, 0.3); margin: 12px 0;">
            <p><strong>💡 Recommandations financières :</strong></p>
            <ul>
                <li><strong>Relance active des clients :</strong> Contactez sans attendre les clients dont les créances arrivent à échéance pour sécuriser les encaissements.</li>
                <li><strong>Surveillance du DSO (Days Sales Outstanding) :</strong> Tout retard de paiement client imprévu peut faire basculer le compte en découvert bancaire.</li>
                <li><strong>Gestion prudente des dépenses :</strong> Reportez les achats non urgents au mois prochain et négociez des délais de règlement auprès de certains fournisseurs.</li>
                <li><strong>Ligne de crédit préventive :</strong> Informez votre banquier pour anticiper une éventuelle facilité de caisse temporaire.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    else:
        # ALERTE ROUGE
        deficit = abs(solde_previsionnel)
        st.markdown(f"""
        <div class="alert-box alert-red">
            <div class="alert-title">🔴 ALERTE DÉFICIT — Risque Imminent de Découvert Bancaire</div>
            <p><strong>Déficit de Trésorerie Estimé : {format_dh(deficit)}</strong> (Solde prévisionnel négatif : {format_dh(solde_previsionnel)}).</p>
            <p><strong>Risque majeur :</strong> Les ressources liquides ne couvrent pas l'intégralité des engagements du mois. Risque d'agios bancaires, de rejet de chèques/prélèvements et de dégradation de la notation bancaire.</p>
            <hr style="border: 0; border-top: 1px solid rgba(239, 68, 68, 0.3); margin: 12px 0;">
            <p><strong>🚨 Plan d'action d'urgence recommandé :</strong></p>
            <ul>
                <li><strong>Mobilisation de créances :</strong> Recourez immédiatement à l'escompte d'effets de commerce ou à l'affacturage (factoring) sur les factures clients émises.</li>
                <li><strong>Négociation d'une autorisation de découvert :</strong> Sollicitez formellement auprès de votre agence bancaire une facilité de caisse ou un crédit de campagne d'au moins {format_dh(round(deficit * 1.2, -2))}.</li>
                <li><strong>Échelonnement négocié des dettes :</strong> Contactez vos fournisseurs stratégiques et les organismes sociaux pour convenir d'un moratoire ou d'un calendrier d'étalement de paiement.</li>
                <li><strong>Apport d'associés :</strong> Si possible, envisagez un apport temporaire en compte courant d'associé pour combler le trou de liquidité.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # ==========================================
    # Graphiques Interactifs
    # ==========================================
    st.markdown("---")
    st.subheader("4. Visualisations Graphiques")

    graph_col1, graph_col2 = st.columns([1.3, 1])

    with graph_col1:
        st.markdown("##### 🌊 Cascade de Trésorerie (Waterfall)")
        # Graphique Waterfall montrant la transition du solde initial au solde prévisionnel
        fig_waterfall = go.Figure(go.Waterfall(
            name="Flux",
            orientation="v",
            measure=["relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"],
            x=[
                "Solde Initial",
                "Règl. Clients",
                "Autres Enc.",
                "Fournisseurs",
                "Salaires",
                "Loyer",
                "Autres Dép.",
                "Solde Final"
            ],
            textposition="outside",
            text=[
                f"{solde_initial:,.0f} DH",
                f"+{reglements_clients:,.0f} DH",
                f"+{autres_encaissements:,.0f} DH",
                f"-{fournisseurs:,.0f} DH",
                f"-{salaires:,.0f} DH",
                f"-{loyer:,.0f} DH",
                f"-{autres_charges:,.0f} DH",
                f"{solde_previsionnel:,.0f} DH"
            ],
            y=[
                solde_initial,
                reglements_clients,
                autres_encaissements,
                -fournisseurs,
                -salaires,
                -loyer,
                -autres_charges,
                solde_previsionnel
            ],
            connector={"line": {"color": "#94a3b8", "width": 1.5}},
            decreasing={"marker": {"color": "#ef4444"}},
            increasing={"marker": {"color": "#10b981"}},
            totals={"marker": {"color": "#0284c7" if solde_previsionnel >= 0 else "#dc2626"}}
        ))

        fig_waterfall.update_layout(
            title="Décomposition des Flux du Mois (en DH)",
            waterfallgap=0.3,
            height=420,
            margin=dict(l=20, r=20, t=50, b=20),
            plot_bgcolor="rgba(248, 250, 252, 0.5)",
            yaxis=dict(title="Montant (DH)", gridcolor="#e2e8f0")
        )
        st.plotly_chart(fig_waterfall, use_container_width=True)

    with graph_col2:
        st.markdown("##### 🥧 Répartition des Décaissements")
        # Donut Chart des dépenses
        labels_depenses = ["Fournisseurs", "Salaires & Charges", "Loyer & Fixes", "Autres Dépenses"]
        valeurs_depenses = [fournisseurs, salaires, loyer, autres_charges]
        couleurs_dep = ["#3b82f6", "#6366f1", "#f59e0b", "#ec4899"]

        fig_pie = go.Figure(data=[go.Pie(
            labels=labels_depenses,
            values=valeurs_depenses,
            hole=.48,
            marker=dict(colors=couleurs_dep),
            textinfo='percent+label',
            hoverinfo='label+value+percent'
        )])
        fig_pie.update_layout(
            title=f"Total Décaissements : {format_dh(total_decaissements)}",
            height=420,
            margin=dict(l=20, r=20, t=50, b=20),
            showlegend=False
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ==========================================
# ONGLET 2 : MACHINE LEARNING & PRÉVISIONS
# ==========================================
with tab_ml:
    st.subheader("🤖 Modélisation Prédictive par Machine Learning")
    st.markdown("""
    Ce module utilise un algorithme d'apprentissage supervisé (**Régression Linéaire Régularisée - Ridge**) 
    entraîné sur les 24 derniers mois de données historiques de l'entreprise pour projeter 
    les flux d'encaissements et de décaissements futurs.
    """)

    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric(
            label="Qualité du Modèle (Score R²)",
            value=f"{metrics_ml['r2_global']:.2%}",
            help="Le R² (coefficient de détermination) mesure la capacité du modèle à expliquer les variations de trésorerie. Plus il est proche de 100%, plus la modélisation est fiable."
        )
    with m_col2:
        st.metric(
            label="Erreur Moyenne (MAE Encaissements)",
            value=format_dh(metrics_ml['mae_encaissements_dh']),
            help="Écart moyen entre les encaissements réels et les prédictions de l'IA (en DH)."
        )
    with m_col3:
        st.metric(
            label="Erreur Moyenne (MAE Décaissements)",
            value=format_dh(metrics_ml['mae_decaissements_dh']),
            help="Écart moyen entre les décaissements réels et les prédictions de l'IA (en DH)."
        )

    st.markdown("---")
    st.subheader("Projections IA pour les 3 Prochains Mois")
    
    # Calcul des prévisions pour les 3 prochains mois à partir du solde courant choisi
    df_futur = modele_ml.prevoir_mois_suivants(nb_mois=3, solde_initial_depart=solde_initial)

    # Affichage du tableau prévisionnel
    df_futur_display = df_futur[[
        "Mois", "Libelle_Mois", "Solde_Initial_DH", 
        "Total_Encaissements_Prevu_DH", "Total_Decaissements_Prevu_DH", 
        "Flux_Net_Prevu_DH", "Solde_Final_Prevu_DH"
    ]].copy()

    df_futur_display.columns = [
        "Mois", "Période", "Solde Début (DH)", 
        "Encaissements IA (DH)", "Décaissements IA (DH)", 
        "Flux Net IA (DH)", "Solde Fin Prévisionnel (DH)"
    ]

    st.dataframe(
        df_futur_display.style.format({
            "Solde Début (DH)": "{:,.2f} DH",
            "Encaissements IA (DH)": "{:,.2f} DH",
            "Décaissements IA (DH)": "{:,.2f} DH",
            "Flux Net IA (DH)": "{:,.2f} DH",
            "Solde Fin Prévisionnel (DH)": "{:,.2f} DH"
        }),
        use_container_width=True
    )

    # Graphique combiné : Historique + Prévisions IA
    st.markdown("##### 📊 Trajectoire Complète : Historique Réel (24 mois) & Projections IA (3 mois)")
    
    df_hist_sub = df_historique[["Mois", "Solde_Final_DH"]].copy()
    df_hist_sub["Type"] = "Historique Réel"
    df_hist_sub.rename(columns={"Solde_Final_DH": "Solde"}, inplace=True)
    
    # Jonction
    dernier_point = pd.DataFrame([{
        "Mois": df_hist_sub["Mois"].iloc[-1],
        "Solde": df_hist_sub["Solde"].iloc[-1],
        "Type": "Prévision IA"
    }])
    
    df_futur_sub = df_futur[["Mois", "Solde_Final_Prevu_DH"]].copy()
    df_futur_sub.rename(columns={"Solde_Final_Prevu_DH": "Solde"}, inplace=True)
    df_futur_sub["Type"] = "Prévision IA"
    df_futur_sub = pd.concat([dernier_point, df_futur_sub], ignore_index=True)

    fig_line = go.Figure()
    
    # Ligne historique
    fig_line.add_trace(go.Scatter(
        x=df_hist_sub["Mois"],
        y=df_hist_sub["Solde"],
        mode="lines+markers",
        name="Historique Réel (24 mois)",
        line=dict(color="#0284c7", width=3),
        marker=dict(size=6)
    ))
    
    # Ligne de prévision IA
    fig_line.add_trace(go.Scatter(
        x=df_futur_sub["Mois"],
        y=df_futur_sub["Solde"],
        mode="lines+markers",
        name="Prévision IA Future",
        line=dict(color="#10b981", width=3, dash="dash"),
        marker=dict(size=8, symbol="diamond")
    ))

    # Ligne de seuil de sécurité
    fig_line.add_hline(
        y=seuil_securite,
        line_dash="dot",
        line_color="#f59e0b",
        annotation_text=f"Seuil de sécurité ({format_dh(seuil_securite)})",
        annotation_position="bottom right"
    )

    # Ligne de découvert (0 DH)
    fig_line.add_hline(
        y=0,
        line_color="#ef4444",
        line_width=1.5,
        annotation_text="Ligne de Découvert (0 DH)",
        annotation_position="top right"
    )

    fig_line.update_layout(
        title="Évolution du Solde de Trésorerie en Dirhams (DH)",
        xaxis_title="Mois",
        yaxis_title="Solde de Trésorerie (DH)",
        hovermode="x unified",
        height=450,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig_line, use_container_width=True)

# ==========================================
# ONGLET 3 : HISTORIQUE DES DONNÉES (24 MOIS)
# ==========================================
with tab_historique:
    st.subheader("📈 Données Historiques Fictives (2024 - 2025)")
    st.markdown("""
    Ce jeu de données simule les 24 derniers mois d'activité d'une PME marocaine.
    Vous pouvez explorer les flux réels constatés ou télécharger la base au format CSV pour Excel.
    """)

    # Statistiques descriptives rapides
    stat1, stat2, stat3, stat4 = st.columns(4)
    with stat1:
        st.metric("Encaissements Mensuels Moyens", format_dh(df_historique["Total_Encaissements_DH"].mean()))
    with stat2:
        st.metric("Décaissements Mensuels Moyens", format_dh(df_historique["Total_Decaissements_DH"].mean()))
    with stat3:
        st.metric("Flux Net Mensuel Moyen", format_dh(df_historique["Flux_Net_DH"].mean()))
    with stat4:
        st.metric("Solde Moyen en Banque", format_dh(df_historique["Solde_Final_DH"].mean()))

    st.markdown("---")

    # Tableau des données historiques
    colonnes_affichage = [
        "Mois", "Libelle_Mois", "Solde_Initial_DH", 
        "Total_Encaissements_DH", "Total_Decaissements_DH", 
        "Flux_Net_DH", "Solde_Final_DH"
    ]
    df_table = df_historique[colonnes_affichage].copy()
    df_table.columns = [
        "Mois", "Libellé", "Solde Initial (DH)", 
        "Encaissements (DH)", "Décaissements (DH)", 
        "Flux Net (DH)", "Solde Final (DH)"
    ]

    st.dataframe(
        df_table.style.format({
            "Solde Initial (DH)": "{:,.2f} DH",
            "Encaissements (DH)": "{:,.2f} DH",
            "Décaissements (DH)": "{:,.2f} DH",
            "Flux Net (DH)": "{:,.2f} DH",
            "Solde Final (DH)": "{:,.2f} DH"
        }),
        height=380,
        use_container_width=True
    )

    # Bouton de téléchargement CSV
    csv_bytes = df_historique.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger l'historique complet (CSV pour Excel)",
        data=csv_bytes,
        file_name="historique_tresorerie_pme_maroc.csv",
        mime="text/csv",
        help="Permet d'ouvrir les données dans Excel pour vos travaux pratiques de gestion financière."
    )

# ==========================================
# ONGLET 4 : GUIDE PÉDAGOGIQUE (GESTION & COMPTABILITÉ)
# ==========================================
with tab_guide:
    st.subheader("📚 Guide de l'Étudiant en Gestion Financière & Comptable")
    st.markdown("""
    Bienvenue dans votre fiche de synthèse académique ! Ce rappel théorique relie directement 
    les calculs effectués par **SmartCash AI** aux concepts enseignés dans votre cursus.
    """)

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown("""
        <div class="pedago-card">
            <h4>1. L'Équation Fondamentale de la Trésorerie</h4>
            <p>Le budget de trésorerie repose sur la comptabilité de trésorerie (flux réels de caisse et banque) :</p>
            <p style="text-align: center; font-weight: bold; font-size: 1.1rem; color: #0284c7; background: #e0f2fe; padding: 10px; border-radius: 8px;">
                Solde de Fin = Solde Initial + Encaissements du Mois - Décaissements du Mois
            </p>
            <ul>
                <li><strong>Encaissement :</strong> Toute entrée réelle de liquidités (règlements clients TTC, emprunts perçus, etc.).</li>
                <li><strong>Décaissement :</strong> Toute sortie réelle de monnaie (fournisseurs TTC, salaires, TVA à payer, etc.).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="pedago-card">
            <h4>2. La Règle d'Or de l'Équilibre Financier (Bilan)</h4>
            <p>La trésorerie nette est l'arbitre entre le long terme et le cycle d'exploitation court terme :</p>
            <p style="text-align: center; font-weight: bold; font-size: 1.05rem; color: #0f172a; background: #f1f5f9; padding: 8px; border-radius: 8px;">
                Trésorerie Nette (TN) = Fonds de Roulement Net Global (FRNG) - Besoin en Fonds de Roulement (BFR)
            </p>
            <ul>
                <li><strong>Si FRNG > BFR :</strong> TN positive (Excédent de trésorerie, situation saine).</li>
                <li><strong>Si FRNG < BFR :</strong> TN négative (Besoin de financement, recours au découvert bancaire).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_g2:
        st.markdown("""
        <div class="pedago-card">
            <h4>3. Résultat Comptable vs Trésorerie : Le Piège Classique</h4>
            <p><strong>Question fréquente aux examens :</strong> <em>"Pourquoi une entreprise bénéficiaire peut-elle faire faillite ?"</em></p>
            <ul>
                <li><strong>Le Résultat (Compte de résultat) :</strong> C'est la différence entre les Produits et les Charges (comptabilité d'engagement). Une vente facturée augmente le résultat même si le client ne paye que dans 90 jours !</li>
                <li><strong>La Trésorerie :</strong> Ne s'intéresse qu'à la monnaie réellement disponible sur le compte en banque.</li>
                <li><strong>Le Risque :</strong> Si les clients payent en retard (crédit client trop long) alors que les fournisseurs exigent un paiement comptant, l'entreprise se retrouve à court de liquidités malgré un bénéfice comptable théorique.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="pedago-card">
            <h4>4. Ratios Clés à Surveiller</h4>
            <ul>
                <li><strong>DSO (Days Sales Outstanding) :</strong> Délai moyen de recouvrement des créances clients :<br>
                <code>(Créances Clients / CA TTC) × 360 jours</code>. Au Maroc, la loi sur les délais de paiement fixe des sanctions en cas de dépassement des 60 à 90 jours.</li>
                <li><strong>DPO (Days Payable Outstanding) :</strong> Délai moyen de règlement des fournisseurs :<br>
                <code>(Dettes Fournisseurs / Achats TTC) × 360 jours</code>.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# Pied de page
# ==========================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding-bottom: 20px;">
    <strong>SmartCash AI</strong> — Application de simulation de trésorerie d'entreprise &bull; Développée pour la Gestion Financière & Comptable &bull; Casablanca, Maroc 🇲🇦
</div>
""", unsafe_allow_html=True)
