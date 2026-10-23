"""
SmartCash - Application de Prévision de Trésorerie
Tableau de bord financier pour PME et gestionnaires financiers au Maroc.
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

# ==============================================================================
# 1. CONFIGURATION DE LA PAGE STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="SmartCash | Prévision de trésorerie",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. DESIGN & STYLES CSS (FOND NOIR #0B0F14, CARTES #151D27, BORDURES #232F3E)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Palette globale & typographie */
    :root {
        --bg-main: #0B0F14;
        --bg-card: #151D27;
        --bg-card-hover: #1A2432;
        --border-subtle: #232F3E;
        --border-focus: #38BDF8;
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
        --accent-blue: #38BDF8;
        --accent-green: #10B981;
        --accent-orange: #F59E0B;
        --accent-red: #EF4444;
    }

    html, body, [class*="css"], .stApp {
        background-color: var(--bg-main) !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--text-primary) !important;
    }

    /* Barre latérale */
    section[data-testid="stSidebar"] {
        background-color: #0E141C !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--text-primary) !important;
        font-weight: 700;
        letter-spacing: -0.3px;
    }

    /* En-tête professionnel du tableau de bord */
    .dashboard-header {
        background: linear-gradient(180deg, #151D27 0%, #101722 100%);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 22px 28px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }
    .header-titles h1 {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: var(--text-primary) !important;
        margin: 0 !important;
        letter-spacing: -0.5px;
    }
    .header-titles p {
        font-size: 0.95rem !important;
        color: var(--accent-blue) !important;
        margin: 4px 0 0 0 !important;
        font-weight: 500;
        letter-spacing: 0.2px;
    }
    .header-badges {
        display: flex;
        gap: 10px;
        align-items: center;
    }
    .header-badge {
        font-size: 0.78rem;
        font-weight: 600;
        padding: 5px 12px;
        border-radius: 6px;
        letter-spacing: 0.3px;
        border: 1px solid var(--border-subtle);
        background: #0B0F14;
        color: var(--text-secondary);
    }
    .header-badge-accent {
        background: rgba(56, 189, 248, 0.1);
        border-color: rgba(56, 189, 248, 0.3);
        color: var(--accent-blue);
    }

    /* Grille des indicateurs financiers (Cartes KPI) */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    @media (max-width: 1024px) {
        .kpi-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    @media (max-width: 640px) {
        .kpi-grid {
            grid-template-columns: 1fr;
        }
    }

    .kpi-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 18px 20px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .kpi-card:hover {
        border-color: #2E3E52;
        transform: translateY(-1px);
    }
    .kpi-card-highlight-green {
        border-top: 3px solid var(--accent-green);
    }
    .kpi-card-highlight-orange {
        border-top: 3px solid var(--accent-orange);
    }
    .kpi-card-highlight-red {
        border-top: 3px solid var(--accent-red);
    }

    .kpi-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: var(--text-secondary);
        margin-bottom: 8px;
    }
    .kpi-value {
        font-family: 'JetBrains Mono', 'Plus Jakarta Sans', monospace;
        font-size: 1.65rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.5px;
        margin-bottom: 6px;
    }
    .kpi-value-blue {
        color: var(--accent-blue);
    }
    .kpi-value-green {
        color: var(--accent-green);
    }
    .kpi-value-orange {
        color: var(--accent-orange);
    }
    .kpi-value-red {
        color: var(--accent-red);
    }
    .kpi-subtext {
        font-size: 0.8rem;
        color: var(--text-muted);
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Section Conteneur Standard */
    .dashboard-panel {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 22px 24px;
        margin-bottom: 24px;
    }
    .panel-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .panel-subtitle {
        font-size: 0.84rem;
        color: var(--text-secondary);
        margin-bottom: 18px;
    }

    /* Boîte d'analyse et recommandations */
    .alert-panel {
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 24px;
        border: 1px solid var(--border-subtle);
        background: var(--bg-card);
    }
    .alert-panel-green {
        border-left: 5px solid var(--accent-green);
        background: linear-gradient(180deg, rgba(16, 185, 129, 0.08) 0%, #151D27 100%);
    }
    .alert-panel-orange {
        border-left: 5px solid var(--accent-orange);
        background: linear-gradient(180deg, rgba(245, 158, 11, 0.08) 0%, #151D27 100%);
    }
    .alert-panel-red {
        border-left: 5px solid var(--accent-red);
        background: linear-gradient(180deg, rgba(239, 68, 68, 0.08) 0%, #151D27 100%);
    }

    .alert-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
        flex-wrap: wrap;
        gap: 8px;
    }
    .alert-status-title {
        font-size: 1.12rem;
        font-weight: 700;
        letter-spacing: -0.2px;
    }
    .title-green { color: var(--accent-green); }
    .title-orange { color: var(--accent-orange); }
    .title-red { color: var(--accent-red); }

    .alert-badge {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-status-green {
        background: rgba(16, 185, 129, 0.15);
        color: var(--accent-green);
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-status-orange {
        background: rgba(245, 158, 11, 0.15);
        color: var(--accent-orange);
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .badge-status-red {
        background: rgba(239, 68, 68, 0.15);
        color: var(--accent-red);
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .alert-explanation {
        font-size: 0.92rem;
        color: var(--text-primary);
        line-height: 1.6;
        margin-bottom: 16px;
    }
    .alert-metrics-strip {
        display: flex;
        gap: 20px;
        padding: 12px 16px;
        background: #0B0F14;
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        margin-bottom: 16px;
        flex-wrap: wrap;
    }
    .strip-item {
        font-size: 0.82rem;
        color: var(--text-secondary);
    }
    .strip-item strong {
        color: var(--text-primary);
        font-family: 'JetBrains Mono', monospace;
    }

    .recommendations-title {
        font-size: 0.88rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--text-secondary);
        margin: 14px 0 8px 0;
    }
    .recommendations-list {
        margin: 0;
        padding-left: 20px;
        color: var(--text-primary);
        font-size: 0.9rem;
        line-height: 1.65;
    }
    .recommendations-list li {
        margin-bottom: 6px;
    }
    .decision-support-note {
        font-size: 0.78rem;
        color: var(--text-muted);
        margin-top: 14px;
        font-style: italic;
        border-top: 1px solid var(--border-subtle);
        padding-top: 10px;
    }

    /* Style des formulaires et widgets natifs Streamlit */
    div[data-baseweb="input"], div[data-baseweb="base-input"] {
        background-color: #0B0F14 !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: var(--accent-blue) !important;
    }
    input {
        color: var(--text-primary) !important;
        font-family: 'JetBrains Mono', 'Plus Jakarta Sans', monospace !important;
    }
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.2px !important;
    }

    /* Boutons */
    .stButton > button {
        background-color: #151D27 !important;
        border: 1px solid var(--border-subtle) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #1E293B !important;
        border-color: var(--accent-blue) !important;
        color: var(--accent-blue) !important;
    }

    /* Onglets Streamlit */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent !important;
        border-bottom: 1px solid var(--border-subtle) !important;
        margin-bottom: 20px !important;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px !important;
        background-color: transparent !important;
        border: none !important;
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0 16px !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent-blue) !important;
        border-bottom: 2px solid var(--accent-blue) !important;
    }

    /* Pied de page */
    .dashboard-footer {
        border-top: 1px solid var(--border-subtle);
        margin-top: 40px;
        padding: 20px 0;
        text-align: center;
        color: var(--text-muted);
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. UTILITAIRES DE FORMATAGE FINANCIER (DIRHAM MAROCAIN - DH)
# ==============================================================================
def format_dh(valeur, show_decimals=False):
    """
    Formate un montant en Dirhams marocains (DH) avec séparateur de milliers.
    Exemples :
      format_dh(25000) -> "25 000 DH"
      format_dh(-12500) -> "- 12 500 DH"
      format_dh(25000.5, show_decimals=True) -> "25 000,50 DH"
    """
    if pd.isna(valeur) or valeur is None:
        return "0 DH"
    
    val = float(valeur)
    signe = "- " if val < 0 else ""
    val_abs = abs(val)
    
    if show_decimals:
        formatted = f"{val_abs:,.2f}".replace(",", " ").replace(".", ",")
    else:
        formatted = f"{int(round(val_abs)):,}".replace(",", " ")
        
    return f"{signe}{formatted} DH"

# ==============================================================================
# 4. CHARGEMENT DES DONNÉES & MODÈLE MACHINE LEARNING
# ==============================================================================
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

# Dernier mois disponible dans l'historique réel
dernier_solde_reel = float(df_historique["Solde_Final_DH"].iloc[-1])
prevision_ia_m1 = modele_ml.prevoir_mois_suivants(nb_mois=1, solde_initial_depart=dernier_solde_reel).iloc[0]

# ==============================================================================
# 5. BARRE LATÉRALE : PARAMÈTRES & SCÉNARIOS
# ==============================================================================
st.sidebar.markdown("### SmartCash")
st.sidebar.caption("Système d'aide à la décision financière")
st.sidebar.markdown("---")

st.sidebar.markdown("#### Scénarios types")
st.sidebar.caption("Chargez une situation financière prédéfinie :")

# Initialisation des variables de session si non existantes
if "solde_init" not in st.session_state:
    st.session_state.solde_init = float(dernier_solde_reel)
if "reglements_clients" not in st.session_state:
    st.session_state.reglements_clients = float(prevision_ia_m1["Total_Encaissements_Prevu_DH"] * 0.90)
if "autres_encaissements" not in st.session_state:
    st.session_state.autres_encaissements = float(prevision_ia_m1["Total_Encaissements_Prevu_DH"] * 0.10)
if "fournisseurs" not in st.session_state:
    st.session_state.fournisseurs = float(prevision_ia_m1["Total_Decaissements_Prevu_DH"] * 0.52)
if "salaires" not in st.session_state:
    st.session_state.salaires = 42000.0
if "loyer" not in st.session_state:
    st.session_state.loyer = 12000.0
if "autres_charges" not in st.session_state:
    st.session_state.autres_charges = 8500.0

col_sc1, col_sc2 = st.sidebar.columns(2)
col_sc3, col_sc4 = st.sidebar.columns(2)

if col_sc1.button("Confort", help="Situation saine avec excédent au-dessus du seuil"):
    st.session_state.solde_init = 120000.0
    st.session_state.reglements_clients = 190000.0
    st.session_state.autres_encaissements = 15000.0
    st.session_state.fournisseurs = 65000.0
    st.session_state.salaires = 40000.0
    st.session_state.loyer = 12000.0
    st.session_state.autres_charges = 8000.0
    st.rerun()

if col_sc2.button("Vigilance", help="Trésorerie positive mais inférieure au seuil de sécurité"):
    st.session_state.solde_init = 18000.0
    st.session_state.reglements_clients = 125000.0
    st.session_state.autres_encaissements = 0.0
    st.session_state.fournisseurs = 78000.0
    st.session_state.salaires = 42000.0
    st.session_state.loyer = 12000.0
    st.session_state.autres_charges = 6000.0
    st.rerun()

if col_sc3.button("Déficit", help="Déficit de trésorerie avec risque de découvert"):
    st.session_state.solde_init = 5000.0
    st.session_state.reglements_clients = 70000.0
    st.session_state.autres_encaissements = 0.0
    st.session_state.fournisseurs = 85000.0
    st.session_state.salaires = 45000.0
    st.session_state.loyer = 12000.0
    st.session_state.autres_charges = 12000.0
    st.rerun()

if col_sc4.button("Prévision IA", help="Applique les montants projetés par le Machine Learning"):
    st.session_state.solde_init = float(dernier_solde_reel)
    st.session_state.reglements_clients = float(prevision_ia_m1["Total_Encaissements_Prevu_DH"] * 0.90)
    st.session_state.autres_encaissements = float(prevision_ia_m1["Total_Encaissements_Prevu_DH"] * 0.10)
    st.session_state.fournisseurs = float(prevision_ia_m1["Total_Decaissements_Prevu_DH"] * 0.52)
    st.session_state.salaires = 42000.0
    st.session_state.loyer = 12000.0
    total_dec_ia = float(prevision_ia_m1["Total_Decaissements_Prevu_DH"])
    st.session_state.autres_charges = max(0.0, float(total_dec_ia - (total_dec_ia * 0.52) - 42000.0 - 12000.0))
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("#### Seuil de sécurité")
seuil_securite = st.sidebar.number_input(
    "Seuil minimum de sécurité (DH) :",
    min_value=0.0,
    max_value=300000.0,
    value=25000.0,
    step=5000.0,
    help="Niveau de réserve en dessous duquel la trésorerie est considérée comme tendue."
)

st.sidebar.markdown("---")
st.sidebar.caption("""
**Méthodologie :**
- **Calcul budgétaire :** Somme arithmétique directe des flux saisis par l'utilisateur.
- **Machine Learning :** Modèle Ridge supervisé entraîné sur 24 mois réels.
""")

# ==============================================================================
# 6. CALCULS FINANCIERS DE BASE (ISSU DES DONNÉES DE SESSION)
# ==============================================================================
solde_initial = float(st.session_state.solde_init)
reglements_clients = float(st.session_state.reglements_clients)
autres_encaissements = float(st.session_state.autres_encaissements)
fournisseurs = float(st.session_state.fournisseurs)
salaires = float(st.session_state.salaires)
loyer = float(st.session_state.loyer)
autres_charges = float(st.session_state.autres_charges)

total_encaissements = reglements_clients + autres_encaissements
total_decaissements = fournisseurs + salaires + loyer + autres_charges
flux_net = total_encaissements - total_decaissements
solde_previsionnel = solde_initial + total_encaissements - total_decaissements

# Ratio d'autonomie financière (jours de couverture des décaissements)
decaissement_journalier = total_decaissements / 30.0 if total_decaissements > 0 else 0.0
if decaissement_journalier > 0 and solde_previsionnel > 0:
    jours_couverture = max(0.0, round(solde_previsionnel / decaissement_journalier, 1))
else:
    jours_couverture = 0.0

# ==============================================================================
# 7. EN-TÊTE PRINCIPAL
# ==============================================================================
st.markdown("""
<div class="dashboard-header">
    <div class="header-titles">
        <h1>SmartCash</h1>
        <p>Prévision de trésorerie</p>
    </div>
    <div class="header-badges">
        <span class="header-badge header-badge-accent">Devise : Dirham marocain (DH)</span>
        <span class="header-badge">Tableau de bord financier</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 8. INDICATEURS FINANCIERS PRINCIPAUX (CARTES MODERNES)
# ==============================================================================
# Détermination du statut pour la carte du solde prévisionnel
if solde_previsionnel > seuil_securite:
    card_highlight = "kpi-card-highlight-green"
    val_class = "kpi-value-green"
    status_label = "Favorable (Au-dessus du seuil)"
elif 0 <= solde_previsionnel <= seuil_securite:
    card_highlight = "kpi-card-highlight-orange"
    val_class = "kpi-value-orange"
    status_label = "Vigilance (Sous le seuil)"
else:
    card_highlight = "kpi-card-highlight-red"
    val_class = "kpi-value-red"
    status_label = "Risque de découvert"

flux_net_symbole = "+" if flux_net >= 0 else "-"
flux_net_formatted = f"{flux_net_symbole} {format_dh(abs(flux_net))}"

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-label">Trésorerie actuelle</div>
        <div class="kpi-value kpi-value-blue">{format_dh(solde_initial)}</div>
        <div class="kpi-subtext">Solde de départ disponible</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Encaissements prévus</div>
        <div class="kpi-value">+ {format_dh(total_encaissements)}</div>
        <div class="kpi-subtext">Règlements clients & divers</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Décaissements prévus</div>
        <div class="kpi-value">- {format_dh(total_decaissements)}</div>
        <div class="kpi-subtext">Fournisseurs, salaires, charges</div>
    </div>
    <div class="kpi-card {card_highlight}">
        <div class="kpi-label">Solde prévisionnel calculé</div>
        <div class="kpi-value {val_class}">{format_dh(solde_previsionnel)}</div>
        <div class="kpi-subtext">Flux net : {flux_net_formatted}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 9. GRAPHIQUE PRINCIPAL : TRAJECTOIRE DE TRÉSORERIE (HISTORIQUE & PRÉVISIONS)
# ==============================================================================
# Prévisions ML pour les 3 prochains mois
df_projections_ml = modele_ml.prevoir_mois_suivants(nb_mois=3, solde_initial_depart=solde_initial)

# Préparation des séries temporelles
df_hist_sub = df_historique[["Mois", "Solde_Final_DH"]].copy()
df_hist_sub.rename(columns={"Solde_Final_DH": "Solde"}, inplace=True)

# Point de transition (mois actuel calculé)
dernier_mois_dt = pd.to_datetime(df_hist_sub["Mois"].iloc[-1])
mois_actuel_str = (dernier_mois_dt + pd.DateOffset(months=1)).strftime("%Y-%m")

# Série des projections ML
df_ml_sub = df_projections_ml[["Mois", "Solde_Final_Prevu_DH"]].copy()
df_ml_sub.rename(columns={"Solde_Final_Prevu_DH": "Solde"}, inplace=True)
point_depart_ia = pd.DataFrame([{
    "Mois": df_hist_sub["Mois"].iloc[-1],
    "Solde": df_hist_sub["Solde"].iloc[-1]
}])
df_ml_curve = pd.concat([point_depart_ia, df_ml_sub], ignore_index=True)

fig_principal = go.Figure()

# 1. Ligne historique (Bleu clair #38BDF8)
fig_principal.add_trace(go.Scatter(
    x=df_hist_sub["Mois"],
    y=df_hist_sub["Solde"],
    mode="lines+markers",
    name="Historique réel (24 mois)",
    line=dict(color="#38BDF8", width=2.5),
    marker=dict(size=5, color="#38BDF8"),
    hovertemplate="%{x}<br>Solde constaté : %{y:,.0f} DH<extra></extra>"
))

# 2. Point spécifique : Budget mensuel saisi par l'utilisateur
fig_principal.add_trace(go.Scatter(
    x=[mois_actuel_str],
    y=[solde_previsionnel],
    mode="markers",
    name="Solde prévisionnel budgété",
    marker=dict(
        size=11,
        color="#10B981" if solde_previsionnel >= seuil_securite else ("#F59E0B" if solde_previsionnel >= 0 else "#EF4444"),
        symbol="circle",
        line=dict(color="#FFFFFF", width=1.5)
    ),
    hovertemplate="%{x}<br>Solde budgété calculé : %{y:,.0f} DH<extra></extra>"
))

# 3. Ligne de prévision Machine Learning (Vert discret en pointillé)
fig_principal.add_trace(go.Scatter(
    x=df_ml_curve["Mois"],
    y=df_ml_curve["Solde"],
    mode="lines+markers",
    name="Prévision Machine Learning (3 mois)",
    line=dict(color="#34D399", width=2, dash="dash"),
    marker=dict(size=7, symbol="diamond", color="#34D399"),
    hovertemplate="%{x}<br>Projection IA : %{y:,.0f} DH<extra></extra>"
))

# 4. Ligne de référence du seuil de sécurité (Orange discret en pointillé)
fig_principal.add_hline(
    y=seuil_securite,
    line_dash="dot",
    line_color="#F59E0B",
    line_width=1.5,
    annotation_text=f"Seuil de sécurité ({format_dh(seuil_securite)})",
    annotation_position="bottom right",
    annotation_font=dict(color="#F59E0B", size=11)
)

# 5. Ligne de référence à zéro (Rouge pour risque de découvert)
fig_principal.add_hline(
    y=0,
    line_color="#EF4444",
    line_width=1.5,
    annotation_text="Ligne de découvert (0 DH)",
    annotation_position="top right",
    annotation_font=dict(color="#EF4444", size=11)
)

fig_principal.update_layout(
    title=dict(
        text="Trajectoire de trésorerie (Historique réel vs Projections en DH)",
        font=dict(color="#F8FAFC", size=14, family="Plus Jakarta Sans")
    ),
    paper_bgcolor="#151D27",
    plot_bgcolor="#151D27",
    font=dict(color="#94A3B8", family="Plus Jakarta Sans"),
    xaxis=dict(
        title="Période (Mois)",
        gridcolor="#1E293B",
        linecolor="#232F3E",
        tickcolor="#94A3B8",
        tickfont=dict(color="#94A3B8", size=11),
        title_font=dict(color="#CBD5E1", size=12)
    ),
    yaxis=dict(
        title="Montant (DH)",
        gridcolor="#1E293B",
        linecolor="#232F3E",
        tickcolor="#94A3B8",
        tickfont=dict(color="#94A3B8", size=11),
        title_font=dict(color="#CBD5E1", size=12),
        zeroline=False
    ),
    hovermode="x unified",
    height=410,
    margin=dict(l=20, r=20, t=50, b=20),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        bgcolor="rgba(21, 29, 39, 0.8)",
        bordercolor="#232F3E",
        font=dict(color="#E5E7EB", size=11)
    )
)

st.plotly_chart(fig_principal, use_container_width=True)

# ==============================================================================
# 10. SECTION « ANALYSE ET RECOMMANDATIONS »
# ==============================================================================
if total_encaissements == 0 and total_decaissements == 0 and solde_initial == 0:
    st.markdown("""
    <div class="alert-panel">
        <div class="alert-status-title">Données insuffisantes</div>
        <p class="alert-explanation">
            Aucun montant n'est actuellement renseigné. Veuillez renseigner votre solde initial, 
            vos encaissements et vos décaissements pour afficher l'analyse financière et les recommandations adaptées.
        </p>
    </div>
    """, unsafe_allow_html=True)

elif solde_previsionnel > seuil_securite:
    # Situation favorable (Vert #10B981)
    marge_securite = solde_previsionnel - seuil_securite
    st.markdown(f"""
    <div class="alert-panel alert-panel-green">
        <div class="alert-header">
            <div class="alert-status-title title-green">Situation favorable — Excédent de trésorerie</div>
            <span class="alert-badge badge-status-green">Risque faible</span>
        </div>
        <p class="alert-explanation">
            Le solde prévisionnel s'établit à <strong>{format_dh(solde_previsionnel)}</strong>, 
            dépassant le seuil de sécurité défini ({format_dh(seuil_securite)}) avec une marge positive 
            de <strong>{format_dh(marge_securite)}</strong>. Les encaissements prévus couvrent l'intégralité 
            des décaissements programmés sur le mois.
        </p>
        <div class="alert-metrics-strip">
            <div class="strip-item">Solde prévisionnel : <strong>{format_dh(solde_previsionnel)}</strong></div>
            <div class="strip-item">Flux net du mois : <strong>{format_dh(flux_net)}</strong></div>
            <div class="strip-item">Autonomie estimée : <strong>{jours_couverture} jours de dépenses</strong></div>
            <div class="strip-item">Seuil de sécurité : <strong>{format_dh(seuil_securite)}</strong></div>
        </div>
        <div class="recommendations-title">Aide à la décision & actions concrètes :</div>
        <ul class="recommendations-list">
            <li><strong>Optimisation des liquidités :</strong> Étudiez le placement à court terme des excédents non immédiatement requis (ex. dépôts à terme ou OPCVM monétaires) afin de valoriser les disponibilités.</li>
            <li><strong>Négociation d'escomptes fournisseurs :</strong> Proposez à vos fournisseurs stratégiques des règlements anticipés en contrepartie d'un escompte commercial (1 % à 2 %).</li>
            <li><strong>Maintien de la vigilance :</strong> Poursuivez le suivi des échéances clients pour préserver cette régularité de trésorerie sans relâcher les délais de relance.</li>
        </ul>
        <div class="decision-support-note">
            Recommandation à titre d'aide à la décision financière : ces repères constituent des orientations prudentes de gestion.
        </div>
    </div>
    """, unsafe_allow_html=True)

elif 0 <= solde_previsionnel <= seuil_securite:
    # Situation de vigilance (Orange #F59E0B)
    deficit_seuil = seuil_securite - solde_previsionnel
    st.markdown(f"""
    <div class="alert-panel alert-panel-orange">
        <div class="alert-header">
            <div class="alert-status-title title-orange">Vigilance — Trésorerie positive mais inférieure au seuil de sécurité</div>
            <span class="alert-badge badge-status-orange">Vigilance requise</span>
        </div>
        <p class="alert-explanation">
            Le solde prévisionnel est positif (<strong>{format_dh(solde_previsionnel)}</strong>), 
            mais il reste inférieur au seuil de sécurité recommandé de <strong>{format_dh(seuil_securite)}</strong> 
            (écart de <strong>{format_dh(deficit_seuil)}</strong>). Le matelas de liquidité disponible est étroit, 
            ce qui expose l'entreprise en cas de décalage imprévu d'un règlement client.
        </p>
        <div class="alert-metrics-strip">
            <div class="strip-item">Solde prévisionnel : <strong>{format_dh(solde_previsionnel)}</strong></div>
            <div class="strip-item">Flux net du mois : <strong>{format_dh(flux_net)}</strong></div>
            <div class="strip-item">Autonomie estimée : <strong>{jours_couverture} jours de dépenses</strong></div>
            <div class="strip-item">Écart au seuil : <strong>- {format_dh(deficit_seuil)}</strong></div>
        </div>
        <div class="recommendations-title">Aide à la décision & actions concrètes :</div>
        <ul class="recommendations-list">
            <li><strong>Relance préventive des clients :</strong> Contactez dès à présent les clients dont les créances arrivent à échéance ce mois-ci pour confirmer les dates de règlement effectives.</li>
            <li><strong>Surveillance des délais de paiement (DSO) :</strong> Évitez tout dépassement des délais accordés pour préserver le niveau d'encaissements prévu.</li>
            <li><strong>Ajustement des décaissements non urgents :</strong> Différez les dépenses facultatives ou rééchelonnez les achats non critiques vers le mois suivant.</li>
            <li><strong>Anticipation bancaire :</strong> Vérifiez la validité de vos autorisations de découvert ou facilités de caisse auprès de votre établissement bancaire pour parer à tout imprévu.</li>
        </ul>
        <div class="decision-support-note">
            Recommandation à titre d'aide à la décision financière : ces repères constituent des orientations prudentes de gestion.
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # Situation de risque réel (Rouge #EF4444)
    deficit_reel = abs(solde_previsionnel)
    st.markdown(f"""
    <div class="alert-panel alert-panel-red">
        <div class="alert-header">
            <div class="alert-status-title title-red">Risque de découvert — Déficit de trésorerie prévu</div>
            <span class="alert-badge badge-status-red">Risque financier avéré</span>
        </div>
        <p class="alert-explanation">
            Les prévisions actuelles aboutissent à un solde négatif de <strong>{format_dh(solde_previsionnel)}</strong>, 
            soit un besoin de financement immédiat de <strong>{format_dh(deficit_reel)}</strong>. 
            Les liquidités initiales et les encaissements prévus ({format_dh(total_encaissements)}) ne permettent pas 
            de couvrir la totalité des décaissements engagés ({format_dh(total_decaissements)}).
        </p>
        <div class="alert-metrics-strip">
            <div class="strip-item">Déficit estimé : <strong>- {format_dh(deficit_reel)}</strong></div>
            <div class="strip-item">Flux net déficitaire : <strong>{format_dh(flux_net)}</strong></div>
            <div class="strip-item">Sorties engagées : <strong>{format_dh(total_decaissements)}</strong></div>
            <div class="strip-item">Entrées attendues : <strong>{format_dh(total_encaissements)}</strong></div>
        </div>
        <div class="recommendations-title">Plan d'action d'urgence recommandé :</div>
        <ul class="recommendations-list">
            <li><strong>Mobilisation accélérée de créances :</strong> Sollicitez l'escompte d'effets de commerce ou le recours à l'affacturage sur les factures clients déjà émises pour débloquer des liquidités sous 48h.</li>
            <li><strong>Aménagement des échéances fournisseurs :</strong> Négociez un étalement de paiement ou un report d'échéance avec les principaux fournisseurs afin de lisser les sorties de fonds.</li>
            <li><strong>Négociation d'une facilité de caisse :</strong> Formalisez une demande d'autorisation de découvert bancaire temporaire d'au moins {format_dh(round(deficit_reel * 1.2, -2))} auprès de votre agence bancaire.</li>
            <li><strong>Priorisation stricte des paiements :</strong> Donnez la priorité absolue aux salaires et aux obligations légales pour éviter tout risque contentieux.</li>
        </ul>
        <div class="decision-support-note">
            Recommandation à titre d'aide à la décision financière : ces repères constituent des orientations prudentes de gestion.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 11. DÉTAILS DE PRÉVISION & GESTION (ONGLETS STRUCTURÉS)
# ==============================================================================
tab_saisie, tab_ml_view, tab_historique_view, tab_guide_view = st.tabs([
    "Saisie du budget mensuel",
    "Projections Machine Learning",
    "Historique des données (24 mois)",
    "Principes de gestion financière"
])

# ------------------------------------------------------------------------------
# ONGLET 1 : SAISIE DU BUDGET MENSUEL & CASCADE DES FLUX
# ------------------------------------------------------------------------------
with tab_saisie:
    st.markdown("##### Paramètres de trésorerie du mois")
    st.caption("Modifiez les montants ci-dessous pour recalculer instantanément le tableau de bord.")

    col_in1, col_in2, col_in3 = st.columns([1, 1.2, 1.2])

    with col_in1:
        st.markdown("**1. Trésorerie de départ**")
        nouveau_solde_init = st.number_input(
            "Solde initial en banque & caisse (DH) :",
            value=float(st.session_state.solde_init),
            step=5000.0,
            key="input_saisie_solde_init",
            help="Disponibilités réelles sur les comptes bancaires et en caisse en début de mois."
        )
        if nouveau_solde_init != st.session_state.solde_init:
            st.session_state.solde_init = nouveau_solde_init
            st.rerun()

    with col_in2:
        st.markdown("**2. Encaissements prévus (Entrées)**")
        nouveaux_reglements = st.number_input(
            "Règlements clients attendus (DH) :",
            value=float(st.session_state.reglements_clients),
            min_value=0.0,
            step=5000.0,
            key="input_saisie_reglements",
            help="Factures clients devant être encaissées au cours du mois."
        )
        nouveaux_autres_enc = st.number_input(
            "Autres encaissements (DH) :",
            value=float(st.session_state.autres_encaissements),
            min_value=0.0,
            step=2000.0,
            key="input_saisie_autres_enc",
            help="Remboursements TVA, subventions, apports ou produits financiers."
        )
        if (nouveaux_reglements != st.session_state.reglements_clients or 
            nouveaux_autres_enc != st.session_state.autres_encaissements):
            st.session_state.reglements_clients = nouveaux_reglements
            st.session_state.autres_encaissements = nouveaux_autres_enc
            st.rerun()

    with col_in3:
        st.markdown("**3. Décaissements prévus (Sorties)**")
        nouveau_frs = st.number_input(
            "Paiements fournisseurs (DH) :",
            value=float(st.session_state.fournisseurs),
            min_value=0.0,
            step=5000.0,
            key="input_saisie_frs"
        )
        nouveau_sal = st.number_input(
            "Salaires & charges sociales (DH) :",
            value=float(st.session_state.salaires),
            min_value=0.0,
            step=2000.0,
            key="input_saisie_sal"
        )
        nouveau_loy = st.number_input(
            "Loyer & charges fixes (DH) :",
            value=float(st.session_state.loyer),
            min_value=0.0,
            step=1000.0,
            key="input_saisie_loy"
        )
        nouveau_aut = st.number_input(
            "Autres décaissements (DH) :",
            value=float(st.session_state.autres_charges),
            min_value=0.0,
            step=1000.0,
            key="input_saisie_aut"
        )
        if (nouveau_frs != st.session_state.fournisseurs or
            nouveau_sal != st.session_state.salaires or
            nouveau_loy != st.session_state.loyer or
            nouveau_aut != st.session_state.autres_charges):
            st.session_state.fournisseurs = nouveau_frs
            st.session_state.salaires = nouveau_sal
            st.session_state.loyer = nouveau_loy
            st.session_state.autres_charges = nouveau_aut
            st.rerun()

    st.markdown("---")
    st.markdown("##### Décomposition détaillée des flux du mois")

    col_g1, col_g2 = st.columns([1.3, 1])

    with col_g1:
        # Cascade de trésorerie (Waterfall)
        fig_waterfall = go.Figure(go.Waterfall(
            name="Flux",
            orientation="v",
            measure=["relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"],
            x=[
                "Solde initial",
                "Règl. clients",
                "Autres enc.",
                "Fournisseurs",
                "Salaires",
                "Loyer & fixes",
                "Autres charges",
                "Solde final"
            ],
            textposition="outside",
            text=[
                format_dh(solde_initial),
                f"+ {format_dh(reglements_clients)}",
                f"+ {format_dh(autres_encaissements)}",
                f"- {format_dh(fournisseurs)}",
                f"- {format_dh(salaires)}",
                f"- {format_dh(loyer)}",
                f"- {format_dh(autres_charges)}",
                format_dh(solde_previsionnel)
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
            connector={"line": {"color": "#475569", "width": 1.5}},
            decreasing={"marker": {"color": "#EF4444"}},
            increasing={"marker": {"color": "#10B981"}},
            totals={"marker": {"color": "#38BDF8" if solde_previsionnel >= 0 else "#EF4444"}}
        ))

        fig_waterfall.update_layout(
            title=dict(
                text="Cascade de transition du solde (en DH)",
                font=dict(color="#F8FAFC", size=13, family="Plus Jakarta Sans")
            ),
            paper_bgcolor="#151D27",
            plot_bgcolor="#151D27",
            font=dict(color="#94A3B8", family="Plus Jakarta Sans"),
            waterfallgap=0.3,
            height=380,
            margin=dict(l=20, r=20, t=50, b=20),
            yaxis=dict(
                title="Montant (DH)",
                gridcolor="#1E293B",
                linecolor="#232F3E",
                tickfont=dict(color="#94A3B8", size=11),
                title_font=dict(color="#CBD5E1", size=12)
            ),
            xaxis=dict(
                tickfont=dict(color="#94A3B8", size=10)
            )
        )
        st.plotly_chart(fig_waterfall, use_container_width=True)

    with col_g2:
        # Donut Chart des charges
        labels_dep = ["Fournisseurs", "Salaires & charges", "Loyer & fixes", "Autres charges"]
        vals_dep = [fournisseurs, salaires, loyer, autres_charges]
        couleurs_dep = ["#38BDF8", "#818CF8", "#F59E0B", "#F43F5E"]

        fig_pie = go.Figure(data=[go.Pie(
            labels=labels_dep,
            values=vals_dep,
            hole=0.55,
            marker=dict(colors=couleurs_dep, line=dict(color="#151D27", width=2)),
            textinfo='percent',
            hoverinfo='label+value+percent'
        )])
        fig_pie.update_layout(
            title=dict(
                text=f"Total décaissements : {format_dh(total_decaissements)}",
                font=dict(color="#F8FAFC", size=13, family="Plus Jakarta Sans")
            ),
            paper_bgcolor="#151D27",
            plot_bgcolor="#151D27",
            font=dict(color="#94A3B8", family="Plus Jakarta Sans"),
            height=380,
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(color="#CBD5E1", size=10)
            )
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ------------------------------------------------------------------------------
# ONGLET 2 : PROJECTIONS MACHINE LEARNING
# ------------------------------------------------------------------------------
with tab_ml_view:
    st.markdown("##### Projections statistiques par Machine Learning")
    st.markdown("""
    Cette modélisation s'appuie sur une **Régression Linéaire Régularisée (Ridge)** entraînée 
    sur les 24 derniers mois d'historique réel. Elle tient compte des composantes cycliques annuelles 
    et de l'inertie des flux passés.
    
    *Important : les projections ci-dessous constituent une modélisation statistique algorithmique, 
    strictement distincte du calcul budgétaire saisi dans l'onglet précédent.*
    """)

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric(
            label="Qualité globale du modèle (R²)",
            value=f"{metrics_ml['r2_global']:.2%}",
            help="Coefficient de détermination : mesure la proportion de variance des flux expliquée par le modèle."
        )
    with col_m2:
        st.metric(
            label="Erreur moyenne (MAE Encaissements)",
            value=format_dh(metrics_ml['mae_encaissements_dh']),
            help="Écart absolu moyen entre les prédictions d'encaissements et les montants constatés."
        )
    with col_m3:
        st.metric(
            label="Erreur moyenne (MAE Décaissements)",
            value=format_dh(metrics_ml['mae_decaissements_dh']),
            help="Écart absolu moyen entre les prédictions de décaissements et les montants constatés."
        )

    st.markdown("---")
    st.markdown("##### Tableau prévisionnel des 3 prochains mois (Modélisation IA)")

    df_display_ml = df_projections_ml[[
        "Mois", "Libelle_Mois", "Solde_Initial_DH",
        "Total_Encaissements_Prevu_DH", "Total_Decaissements_Prevu_DH",
        "Flux_Net_Prevu_DH", "Solde_Final_Prevu_DH"
    ]].copy()

    df_display_ml.columns = [
        "Mois", "Période", "Solde initial (DH)",
        "Encaissements prévus (DH)", "Décaissements prévus (DH)",
        "Flux net prévu (DH)", "Solde final prévu (DH)"
    ]

    st.dataframe(
        df_display_ml.style.format({
            "Solde initial (DH)": lambda v: format_dh(v),
            "Encaissements prévus (DH)": lambda v: format_dh(v),
            "Décaissements prévus (DH)": lambda v: format_dh(v),
            "Flux net prévu (DH)": lambda v: format_dh(v),
            "Solde final prévu (DH)": lambda v: format_dh(v)
        }),
        use_container_width=True
    )

# ------------------------------------------------------------------------------
# ONGLET 3 : HISTORIQUE DES DONNÉES (24 MOIS)
# ------------------------------------------------------------------------------
with tab_historique_view:
    st.markdown("##### Données historiques d'activité (24 mois)")
    st.caption("Base de données chronologique servant à l'entraînement du modèle prédictif.")

    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    with col_h1:
        st.metric("Encaissements moyens / mois", format_dh(df_historique["Total_Encaissements_DH"].mean()))
    with col_h2:
        st.metric("Décaissements moyens / mois", format_dh(df_historique["Total_Decaissements_DH"].mean()))
    with col_h3:
        st.metric("Flux net mensuel moyen", format_dh(df_historique["Flux_Net_DH"].mean()))
    with col_h4:
        st.metric("Solde moyen constaté", format_dh(df_historique["Solde_Final_DH"].mean()))

    st.markdown("---")

    df_hist_table = df_historique[[
        "Mois", "Libelle_Mois", "Solde_Initial_DH",
        "Total_Encaissements_DH", "Total_Decaissements_DH",
        "Flux_Net_DH", "Solde_Final_DH"
    ]].copy()

    df_hist_table.columns = [
        "Mois", "Période", "Solde initial (DH)",
        "Encaissements (DH)", "Décaissements (DH)",
        "Flux net (DH)", "Solde final (DH)"
    ]

    st.dataframe(
        df_hist_table.style.format({
            "Solde initial (DH)": lambda v: format_dh(v),
            "Encaissements (DH)": lambda v: format_dh(v),
            "Décaissements (DH)": lambda v: format_dh(v),
            "Flux net (DH)": lambda v: format_dh(v),
            "Solde final (DH)": lambda v: format_dh(v)
        }),
        height=360,
        use_container_width=True
    )

    csv_data = df_historique.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Exporter l'historique complet (CSV)",
        data=csv_data,
        file_name="smartcash_historique_tresorerie.csv",
        mime="text/csv",
        help="Télécharge le jeu de données pour une utilisation dans Excel ou un outil d'audit."
    )

# ------------------------------------------------------------------------------
# ONGLET 4 : PRINCIPES DE GESTION FINANCIÈRE
# ------------------------------------------------------------------------------
with tab_guide_view:
    st.markdown("##### Repères académiques de gestion financière")
    st.caption("Rappels méthodologiques reliant les calculs du tableau de bord aux concepts fondamentaux de finance d'entreprise.")

    col_ped1, col_ped2 = st.columns(2)

    with col_ped1:
        st.markdown("""
        <div style="background: #151D27; border: 1px solid #232F3E; border-radius: 10px; padding: 18px 20px; margin-bottom: 16px;">
            <h4 style="color: #F8FAFC; margin-top: 0; font-size: 0.95rem;">1. L'Équation fondamentale de la trésorerie</h4>
            <p style="color: #CBD5E1; font-size: 0.88rem; line-height: 1.55;">
                Le budget de trésorerie relève de la comptabilité de caisse et enregistre exclusivement les mouvements monétaires réels :
            </p>
            <div style="background: #0B0F14; border: 1px solid #232F3E; padding: 10px 14px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #38BDF8; text-align: center; margin: 12px 0;">
                Solde de Fin = Solde Initial + Encaissements - Décaissements
            </div>
            <ul style="color: #CBD5E1; font-size: 0.85rem; line-height: 1.6; margin-bottom: 0;">
                <li><strong>Encaissement :</strong> Flux entrant effectif de monnaie (règlements clients TTC, cessions d'actifs, déblocages d'emprunts).</li>
                <li><strong>Décaissement :</strong> Sortie effective de trésorerie (fournisseurs TTC, salaires nets, cotisations sociales, TVA à reverser).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: #151D27; border: 1px solid #232F3E; border-radius: 10px; padding: 18px 20px; margin-bottom: 16px;">
            <h4 style="color: #F8FAFC; margin-top: 0; font-size: 0.95rem;">2. Équilibre financier fonctionnel</h4>
            <p style="color: #CBD5E1; font-size: 0.88rem; line-height: 1.55;">
                La trésorerie nette traduit l'adéquation entre les ressources stables et les besoins d'exploitation :
            </p>
            <div style="background: #0B0F14; border: 1px solid #232F3E; padding: 10px 14px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #F8FAFC; text-align: center; margin: 12px 0;">
                Trésorerie Nette (TN) = FRNG - BFR
            </div>
            <ul style="color: #CBD5E1; font-size: 0.85rem; line-height: 1.6; margin-bottom: 0;">
                <li><strong>FRNG > BFR :</strong> Trésorerie nette positive. L'excédent de ressources stables finance l'intégralité du cycle d'exploitation.</li>
                <li><strong>FRNG < BFR :</strong> Trésorerie nette négative. L'entreprise doit mobiliser des concours bancaires à court terme (découvert, facilités de caisse).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_ped2:
        st.markdown("""
        <div style="background: #151D27; border: 1px solid #232F3E; border-radius: 10px; padding: 18px 20px; margin-bottom: 16px;">
            <h4 style="color: #F8FAFC; margin-top: 0; font-size: 0.95rem;">3. Résultat comptable vs Trésorerie</h4>
            <p style="color: #CBD5E1; font-size: 0.88rem; line-height: 1.55;">
                Une entreprise peut être comptablement bénéficiaire tout en connaissant une crise de liquidité majeure :
            </p>
            <ul style="color: #CBD5E1; font-size: 0.85rem; line-height: 1.6; margin-bottom: 0;">
                <li><strong>Le compte de résultat</strong> enregistre les produits et charges dès leur engagement juridique (facturation), indépendamment du paiement effectif.</li>
                <li><strong>La trésorerie</strong> ne comptabilise que la monnaie disponible. Si les délais clients s'allongent (DSO élevé) alors que les fournisseurs exigent un règlement comptant, l'entreprise s'expose au risque de cessation de paiements malgré un résultat positif.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: #151D27; border: 1px solid #232F3E; border-radius: 10px; padding: 18px 20px; margin-bottom: 16px;">
            <h4 style="color: #F8FAFC; margin-top: 0; font-size: 0.95rem;">4. Indicateurs opérationnels de suivi</h4>
            <ul style="color: #CBD5E1; font-size: 0.85rem; line-height: 1.6; margin-bottom: 0;">
                <li><strong>DSO (Days Sales Outstanding) :</strong> Délai moyen d'encaissement des créances clients : <code>(Créances TTC / CA TTC) × 360 jours</code>. Au Maroc, la législation sur les délais de paiement encadre strictement les délais interentreprises.</li>
                <li><strong>DPO (Days Payable Outstanding) :</strong> Délai moyen de paiement accordé par les fournisseurs : <code>(Dettes Fournisseurs TTC / Achats TTC) × 360 jours</code>.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 12. PIED DE PAGE
# ==============================================================================
st.markdown("""
<div class="dashboard-footer">
    SmartCash &bull; Système d'aide à la décision financière pour PME &bull; Casablanca, Maroc &bull; Devise : DH
</div>
""", unsafe_allow_html=True)
