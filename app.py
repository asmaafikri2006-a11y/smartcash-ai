"""
SmartCash AI - Gestion et prévision de trésorerie
Tableau de bord financier pour PME et gestionnaires au Maroc.
Devise : Dirham marocain (DH).
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
import io

from data_importer import (
    detecter_colonnes,
    valider_et_traiter_operations,
    calculer_solde_cumule,
    generer_donnees_demo_operations,
    generer_modele_csv,
    generer_modele_excel
)
from data_generator import charger_ou_generer_donnees
from ml_model import ModelePrevisionTresorerie

# ==============================================================================
# 1. CONFIGURATION DE LA PAGE STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="SmartCash AI | Gestion et prévision de trésorerie",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. DESIGN & STYLES CSS (FOND CLAIR #F1F5F9, CARTES #FFFFFF, BLEU MARINE #17365D, TURQUOISE #087F8C)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg-main: #F1F5F9;
        --bg-card: #FFFFFF;
        --border-subtle: #DCE5EF;
        --text-navy: #17365D;
        --text-body: #334155;
        --text-muted: #64748B;
        --accent-turquoise: #087F8C;
        --accent-orange: #D97706;
        --accent-red: #DC2626;
    }

    html, body, [class*="css"], .stApp {
        background-color: var(--bg-main) !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--text-body) !important;
    }

    /* Barre latérale */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    /* En-tête de l'application */
    .app-header {
        background: #FFFFFF;
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 22px 28px;
        margin-bottom: 24px;
        box-shadow: 0 2px 8px rgba(23, 54, 93, 0.04);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }
    .header-titles h1 {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: var(--text-navy) !important;
        margin: 0 !important;
        letter-spacing: -0.5px;
    }
    .header-titles p {
        font-size: 0.95rem !important;
        color: var(--accent-turquoise) !important;
        margin: 4px 0 0 0 !important;
        font-weight: 600;
        letter-spacing: 0.1px;
    }
    .header-badges {
        display: flex;
        gap: 10px;
        align-items: center;
    }
    .header-badge {
        font-size: 0.78rem;
        font-weight: 600;
        padding: 6px 12px;
        border-radius: 6px;
        border: 1px solid var(--border-subtle);
        background: #F8FAFC;
        color: var(--text-navy);
    }

    /* Conteneur de section en carte blanche */
    .content-card {
        background: #FFFFFF;
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 2px 8px rgba(23, 54, 93, 0.04);
    }
    .card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--text-navy);
        margin: 0 0 6px 0;
        letter-spacing: -0.3px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .card-subtitle {
        font-size: 0.85rem;
        color: var(--text-muted);
        margin: 0 0 18px 0;
    }

    /* Grille des indicateurs financiers */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 14px;
        margin-bottom: 24px;
    }
    @media (max-width: 1200px) {
        .kpi-container {
            grid-template-columns: repeat(3, 1fr);
        }
    }
    @media (max-width: 768px) {
        .kpi-container {
            grid-template-columns: 1fr;
        }
    }

    .kpi-box {
        background: #FFFFFF;
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 18px 18px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 1px 4px rgba(23, 54, 93, 0.03);
    }
    .kpi-box-turquoise {
        border-top: 3px solid var(--accent-turquoise);
    }
    .kpi-box-orange {
        border-top: 3px solid var(--accent-orange);
    }
    .kpi-box-red {
        border-top: 3px solid var(--accent-red);
    }
    .kpi-box-navy {
        border-top: 3px solid var(--text-navy);
    }

    .kpi-title {
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--text-muted);
        margin-bottom: 6px;
    }
    .kpi-number {
        font-family: 'JetBrains Mono', 'Plus Jakarta Sans', monospace;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--text-navy);
        letter-spacing: -0.4px;
        margin-bottom: 4px;
    }
    .kpi-number-turquoise { color: var(--accent-turquoise); }
    .kpi-number-orange { color: var(--accent-orange); }
    .kpi-number-red { color: var(--accent-red); }

    .kpi-foot {
        font-size: 0.78rem;
        color: var(--text-muted);
    }

    /* Boîtes d'alertes & Recommandations */
    .alert-card {
        border-radius: 10px;
        padding: 20px 24px;
        margin-top: 14px;
        border: 1px solid var(--border-subtle);
    }
    .alert-favorable {
        background: #F0FDFA;
        border-left: 5px solid var(--accent-turquoise);
    }
    .alert-vigilance {
        background: #FFFBEB;
        border-left: 5px solid var(--accent-orange);
    }
    .alert-danger {
        background: #FEF2F2;
        border-left: 5px solid var(--accent-red);
    }

    .alert-heading {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .heading-turquoise { color: #0F766E; }
    .heading-orange { color: #B45309; }
    .heading-red { color: #B91C1C; }

    .alert-text {
        font-size: 0.9rem;
        color: var(--text-body);
        line-height: 1.6;
        margin-bottom: 12px;
    }
    .alert-actions-title {
        font-size: 0.84rem;
        font-weight: 700;
        text-transform: uppercase;
        color: var(--text-navy);
        margin-top: 10px;
        margin-bottom: 6px;
        letter-spacing: 0.3px;
    }
    .alert-actions-list {
        margin: 0;
        padding-left: 18px;
        font-size: 0.88rem;
        color: var(--text-body);
        line-height: 1.6;
    }
    .alert-disclaimer {
        font-size: 0.78rem;
        color: var(--text-muted);
        margin-top: 12px;
        font-style: italic;
        border-top: 1px solid rgba(0, 0, 0, 0.06);
        padding-top: 8px;
    }

    /* Style des inputs & boutons */
    div[data-baseweb="input"], div[data-baseweb="base-input"] {
        background-color: #FFFFFF !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        color: var(--text-navy) !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: var(--accent-turquoise) !important;
    }
    input {
        color: var(--text-navy) !important;
        font-family: 'JetBrains Mono', 'Plus Jakarta Sans', monospace !important;
    }
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        color: var(--text-navy) !important;
        font-weight: 600 !important;
        font-size: 0.84rem !important;
    }

    .stButton > button {
        background-color: #17365D !important;
        color: #FFFFFF !important;
        border: 1px solid #17365D !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #087F8C !important;
        border-color: #087F8C !important;
        color: #FFFFFF !important;
    }

    /* Badges de table */
    .badge-enc {
        background: #CCFBF1;
        color: #0F766E;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-dec {
        background: #FEE2E2;
        color: #991B1B;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    .footer-bar {
        border-top: 1px solid var(--border-subtle);
        margin-top: 36px;
        padding: 18px 0;
        text-align: center;
        color: var(--text-muted);
        font-size: 0.82rem;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. UTILITAIRE DE FORMATAGE FINANCIER EN DIRHAMS (DH)
# ==============================================================================
def format_dh(valeur, show_decimals=True):
    """
    Formate un montant en Dirhams marocains : par exemple « 25 000,00 DH ».
    """
    if valeur is None or pd.isna(valeur):
        return "Non renseigné"
    val = float(valeur)
    signe = "- " if val < 0 else ""
    val_abs = abs(val)
    if show_decimals:
        formatted = f"{val_abs:,.2f}".replace(",", " ").replace(".", ",")
    else:
        formatted = f"{int(round(val_abs)):,}".replace(",", " ")
    return f"{signe}{formatted} DH"

# ==============================================================================
# 4. GESTION DE LA SESSION & DES DONNÉES
# ==============================================================================
if "solde_initial_user" not in st.session_state:
    st.session_state.solde_initial_user = 50000.0
if "solde_initial_connu" not in st.session_state:
    st.session_state.solde_initial_connu = True
if "seuil_securite" not in st.session_state:
    st.session_state.seuil_securite = 25000.0
if "raw_uploaded_df" not in st.session_state:
    st.session_state.raw_uploaded_df = None
if "last_file_signature" not in st.session_state:
    st.session_state.last_file_signature = None
if "source_donnees" not in st.session_state:
    st.session_state.source_donnees = "demo"  # 'demo' ou 'import'

# Chargement initial des données de démonstration par défaut
if "operations_valides" not in st.session_state or st.session_state.operations_valides is None:
    df_demo_init = generer_donnees_demo_operations()
    mapping_demo = detecter_colonnes(df_demo_init.columns)
    df_clean_demo, _, _ = valider_et_traiter_operations(
        df_demo_init, mapping_demo['date'], mapping_demo['libelle'], mapping_demo['type'], mapping_demo['montant']
    )
    st.session_state.operations_valides = df_clean_demo
    st.session_state.erreurs_import = []
    st.session_state.stats_import = {"total_lignes": len(df_demo_init), "lignes_valides": len(df_clean_demo), "nb_erreurs": 0}

# ==============================================================================
# 5. BARRE LATÉRALE : PARAMÈTRES GÉNÉRAUX & SEUIL DE SÉCURITÉ
# ==============================================================================
st.sidebar.markdown("### SmartCash AI")
st.sidebar.caption("Gestion et prévision de trésorerie")
st.sidebar.markdown("---")

st.sidebar.markdown("#### Paramètres financiers")

solde_connu = st.sidebar.checkbox(
    "Solde initial connu",
    value=st.session_state.solde_initial_connu,
    help="Décochez cette option si le solde de départ en banque est inconnu au début de la période."
)
st.session_state.solde_initial_connu = solde_connu

if solde_connu:
    solde_in_val = st.sidebar.number_input(
        "Solde initial disponible (DH) :",
        value=float(st.session_state.solde_initial_user),
        step=5000.0,
        help="Montant disponible sur vos comptes bancaires et en caisse en début de période."
    )
    st.session_state.solde_initial_user = solde_in_val
else:
    st.sidebar.info("Le solde initial est marqué comme inconnu. Le solde final ne pourra pas être déterminé avec certitude.")

seuil_sec_val = st.sidebar.number_input(
    "Seuil de sécurité minimum (DH) :",
    min_value=0.0,
    max_value=500000.0,
    value=float(st.session_state.seuil_securite),
    step=5000.0,
    help="Seuil de réserve en dessous duquel la trésorerie est jugée tendue."
)
st.session_state.seuil_securite = seuil_sec_val

st.sidebar.markdown("---")
st.sidebar.caption("""
**Règles de gestion :**
- Les opérations sont classées en **Encaissement** (+) et **Décaissement** (-).
- Le solde net = Encaissements − Décaissements.
- Le solde final = Solde initial + Encaissements − Décaissements.
""")

# ==============================================================================
# 6. EN-TÊTE PRINCIPAL
# ==============================================================================
st.markdown("""
<div class="app-header">
    <div class="header-titles">
        <h1>SmartCash AI</h1>
        <p>Gestion et prévision de trésorerie</p>
    </div>
    <div class="header-badges">
        <span class="header-badge">Devise : Dirham marocain (DH)</span>
        <span class="header-badge" style="background:#F0FDFA; color:#0F766E; border-color:#99F6E4;">Module PME</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 7. SECTION 1 : IMPORTATION DES OPÉRATIONS COMPTABLES (OBJECTIF 2)
# ==============================================================================
with st.container():
    st.markdown("""
    <div class="content-card">
        <div class="card-title">Importer les opérations comptables</div>
        <div class="card-subtitle">Chargez votre relevé ou journal d'opérations au format CSV ou Excel (.xlsx).</div>
    """, unsafe_allow_html=True)

    col_upload, col_templates = st.columns([2, 1.2])

    with col_upload:
        uploaded_file = st.file_uploader(
            "Sélectionner un fichier (CSV ou Excel) :",
            type=["csv", "xlsx", "xls"],
            key="file_uploader_operations",
            help="Le fichier doit comporter les colonnes : Date, Libellé, Type (Encaissement/Décaissement) et Montant."
        )

    with col_templates:
        st.markdown("**Modèles prêts à l'emploi :**")
        st.caption("Téléchargez un modèle préformaté avec exemples :")
        c_dl1, c_dl2 = st.columns(2)
        with c_dl1:
            st.download_button(
                label="Modèle CSV",
                data=generer_modele_csv(),
                file_name="modele_operations_smartcash.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c_dl2:
            st.download_button(
                label="Modèle Excel",
                data=generer_modele_excel(),
                file_name="modele_operations_smartcash.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        if st.button("Charger les données de démonstration", use_container_width=True):
            df_demo = generer_donnees_demo_operations()
            m_demo = detecter_colonnes(df_demo.columns)
            df_clean_demo, err_demo, stats_demo = valider_et_traiter_operations(
                df_demo, m_demo['date'], m_demo['libelle'], m_demo['type'], m_demo['montant']
            )
            st.session_state.operations_valides = df_clean_demo
            st.session_state.erreurs_import = err_demo
            st.session_state.stats_import = stats_demo
            st.session_state.source_donnees = "demo"
            st.session_state.raw_uploaded_df = None
            st.rerun()

    # Traitement du fichier importé
    if uploaded_file is not None:
        file_signature = f"{uploaded_file.name}_{uploaded_file.size}"
        # Détection d'un nouveau fichier pour ne pas conserver les données précédentes
        if file_signature != st.session_state.last_file_signature:
            st.session_state.last_file_signature = file_signature
            st.session_state.source_donnees = "import"
            try:
                if uploaded_file.name.lower().endswith(('.xlsx', '.xls')):
                    raw_df = pd.read_excel(uploaded_file, engine='openpyxl')
                else:
                    # Lecture CSV robuste (gestion de séparateurs , et ;)
                    uploaded_file.seek(0)
                    try:
                        raw_df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8')
                    except Exception:
                        uploaded_file.seek(0)
                        raw_df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='latin1')
                st.session_state.raw_uploaded_df = raw_df
            except Exception as e:
                st.error(f"Erreur lors de la lecture du fichier : {e}")
                st.session_state.raw_uploaded_df = None

        if st.session_state.raw_uploaded_df is not None:
            raw_df = st.session_state.raw_uploaded_df
            st.markdown("---")
            st.markdown("##### Correspondance et vérification des colonnes")

            # Détection automatique
            mapping_auto = detecter_colonnes(raw_df.columns)
            colonnes_dispos = list(raw_df.columns)

            c_map1, c_map2, c_map3, c_map4 = st.columns(4)
            with c_map1:
                idx_date = colonnes_dispos.index(mapping_auto['date']) if mapping_auto['date'] in colonnes_dispos else 0
                col_sel_date = st.selectbox("Colonne Date :", colonnes_dispos, index=idx_date)
            with c_map2:
                idx_lib = colonnes_dispos.index(mapping_auto['libelle']) if mapping_auto['libelle'] in colonnes_dispos else (1 if len(colonnes_dispos) > 1 else 0)
                col_sel_lib = st.selectbox("Colonne Libellé :", colonnes_dispos, index=idx_lib)
            with c_map3:
                idx_typ = colonnes_dispos.index(mapping_auto['type']) if mapping_auto['type'] in colonnes_dispos else (2 if len(colonnes_dispos) > 2 else 0)
                col_sel_type = st.selectbox("Colonne Type :", colonnes_dispos, index=idx_typ)
            with c_map4:
                idx_mnt = colonnes_dispos.index(mapping_auto['montant']) if mapping_auto['montant'] in colonnes_dispos else (3 if len(colonnes_dispos) > 3 else 0)
                col_sel_montant = st.selectbox("Colonne Montant :", colonnes_dispos, index=idx_mnt)

            # Validation des lignes
            df_valide, erreurs_trouvees, stats_v = valider_et_traiter_operations(
                raw_df, col_sel_date, col_sel_lib, col_sel_type, col_sel_montant
            )

            st.session_state.operations_valides = df_valide
            st.session_state.erreurs_import = erreurs_trouvees
            st.session_state.stats_import = stats_v

            # Rapport d'intégrité
            if stats_v['nb_erreurs'] == 0:
                st.success(f"Fichier validé avec succès : **{stats_v['lignes_valides']} opérations conformes** prêtes à être analysées.")
            else:
                st.warning(f"Validation partielle : **{stats_v['lignes_valides']} lignes valides** retenues sur {stats_v['total_lignes']} au total ({stats_v['nb_erreurs']} anomalies détectées).")
                with st.expander("Consulter le détail des anomalies détectées"):
                    for err in erreurs_trouvees[:20]:
                        st.write(f"- {err}")
                    if len(erreurs_trouvees) > 20:
                        st.caption(f"... et {len(erreurs_trouvees) - 20} autres anomalies.")

    st.markdown("</div>", unsafe_allow_html=True)

# Vérification de l'existence d'opérations
df_ops = st.session_state.operations_valides
if df_ops is None or df_ops.empty:
    st.info("Aucune opération disponible. Veuillez importer un fichier CSV/Excel ou charger les données de démonstration ci-dessus.")
    st.stop()

# ==============================================================================
# 8. SECTION 2 : INDICATEURS FINANCIERS & CALCULS AUTOMATIQUES (OBJECTIF 3)
# ==============================================================================
solde_initial = float(st.session_state.solde_initial_user) if st.session_state.solde_initial_connu else None
total_encaissements = float(df_ops[df_ops['Type'] == 'Encaissement']['Montant'].sum())
total_decaissements = float(df_ops[df_ops['Type'] == 'Décaissement']['Montant'].sum())
solde_net = total_encaissements - total_decaissements

if solde_initial is not None:
    solde_final = solde_initial + solde_net
else:
    solde_final = None

# Détermination du statut visuel du solde final
if solde_final is not None:
    if solde_final > st.session_state.seuil_securite:
        box_class_final = "kpi-box-turquoise"
        num_class_final = "kpi-number-turquoise"
        statut_libelle = "Favorable (Au-dessus du seuil)"
    elif 0 <= solde_final <= st.session_state.seuil_securite:
        box_class_final = "kpi-box-orange"
        num_class_final = "kpi-number-orange"
        statut_libelle = "Vigilance (Inférieur au seuil)"
    else:
        box_class_final = "kpi-box-red"
        num_class_final = "kpi-number-red"
        statut_libelle = "Risque de découvert bancaire"
else:
    box_class_final = "kpi-box-navy"
    num_class_final = ""
    statut_libelle = "Solde initial non renseigné"

net_class = "kpi-number-turquoise" if solde_net >= 0 else "kpi-number-red"
net_prefix = "+" if solde_net >= 0 else ""

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-box kpi-box-navy">
        <div class="kpi-title">Solde initial</div>
        <div class="kpi-number">{format_dh(solde_initial)}</div>
        <div class="kpi-foot">{"Disponibilités en banque" if solde_initial is not None else "Montant non précisé"}</div>
    </div>
    <div class="kpi-box kpi-box-turquoise">
        <div class="kpi-title">Total Encaissements</div>
        <div class="kpi-number kpi-number-turquoise">+ {format_dh(total_encaissements)}</div>
        <div class="kpi-foot">{len(df_ops[df_ops['Type'] == 'Encaissement'])} règlements reçus</div>
    </div>
    <div class="kpi-box kpi-box-navy">
        <div class="kpi-title">Total Décaissements</div>
        <div class="kpi-number">- {format_dh(total_decaissements)}</div>
        <div class="kpi-foot">{len(df_ops[df_ops['Type'] == 'Décaissement'])} sorties de fonds</div>
    </div>
    <div class="kpi-box kpi-box-navy">
        <div class="kpi-title">Solde net de période</div>
        <div class="kpi-number {net_class}">{net_prefix}{format_dh(solde_net)}</div>
        <div class="kpi-foot">Encaissements − Décaissements</div>
    </div>
    <div class="kpi-box {box_class_final}">
        <div class="kpi-title">Solde final calculé</div>
        <div class="kpi-number {num_class_final}">{format_dh(solde_final)}</div>
        <div class="kpi-foot">{statut_libelle}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 9. SECTION 3 : TABLEAU DES OPÉRATIONS CHRONOLOGIQUES (OBJECTIF 2 & 3)
# ==============================================================================
df_chronologique = calculer_solde_cumule(df_ops, solde_initial)

st.markdown("""
<div class="content-card">
    <div class="card-title">Tableau des opérations comptables</div>
    <div class="card-subtitle">Opérations classées par ordre chronologique avec calcul du solde cumulé ligne par ligne.</div>
""", unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns([1.5, 2, 1.5])
with col_f1:
    filtre_type = st.selectbox("Filtrer par type :", ["Tous", "Encaissements", "Décaissements"])
with col_f2:
    recherche_lib = st.text_input("Rechercher dans les libellés :", placeholder="Ex: Client, Salaire, Loyer...")
with col_f3:
    st.write("")
    st.write(f"**{len(df_chronologique)} opérations au total**")

# Application des filtres
df_vue = df_chronologique.copy()
if filtre_type == "Encaissements":
    df_vue = df_vue[df_vue['Type'] == 'Encaissement']
elif filtre_type == "Décaissements":
    df_vue = df_vue[df_vue['Type'] == 'Décaissement']

if recherche_lib:
    df_vue = df_vue[df_vue['Libellé'].str.contains(recherche_lib, case=False, na=False)]

# Formatage pour affichage dans le tableau
df_table_display = df_vue.copy()
df_table_display['Date'] = pd.to_datetime(df_table_display['Date']).dt.strftime('%d/%m/%Y')

formatters = {
    'Montant': lambda x: format_dh(x),
    'Solde_Cumule_DH': lambda x: format_dh(x) if x is not None else "Indéterminé"
}

df_table_display.rename(columns={
    'Solde_Cumule_DH': 'Solde Cumulé (DH)',
    'Montant': 'Montant (DH)'
}, inplace=True)

st.dataframe(
    df_table_display.style.format({
        'Montant (DH)': lambda x: format_dh(x),
        'Solde Cumulé (DH)': lambda x: format_dh(x) if pd.notna(x) else "Indéterminé"
    }),
    use_container_width=True,
    height=320
)

# Export des opérations nettoyées en CSV
csv_export = df_chronologique.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
st.download_button(
    label="Exporter les opérations traitées (CSV)",
    data=csv_export,
    file_name="smartcash_operations_traitees.csv",
    mime="text/csv"
)

st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 10. SECTION 4 : GRAPHIQUES D'ANALYSE PROFESSIONNELS (OBJECTIF 4)
# ==============================================================================
st.markdown("""
<div class="content-card">
    <div class="card-title">Graphiques d'analyse de trésorerie</div>
    <div class="card-subtitle">Visualisation chronologique des flux et trajectoire du solde cumulé.</div>
""", unsafe_allow_html=True)

col_chart1, col_chart2 = st.columns([1.6, 1.2])

with col_chart1:
    st.markdown("**Évolution de la trésorerie dans le temps**")
    
    if solde_initial is not None and not df_chronologique.empty:
        # Agrégation par jour pour une courbe fluide
        df_daily = df_chronologique.groupby(df_chronologique['Date'].dt.date)['Solde_Cumule_DH'].last().reset_index()
        
        fig_evol = go.Figure()
        
        # Courbe principale (Turquoise #087F8C)
        fig_evol.add_trace(go.Scatter(
            x=df_daily['Date'],
            y=df_daily['Solde_Cumule_DH'],
            mode='lines+markers',
            name='Solde Cumulé (DH)',
            line=dict(color='#087F8C', width=2.5),
            marker=dict(size=6, color='#17365D'),
            hovertemplate='%{x|%d/%m/%Y}<br>Solde : %{y:,.2f} DH<extra></extra>'
        ))
        
        # Ligne de seuil de sécurité (Orange #D97706)
        fig_evol.add_hline(
            y=st.session_state.seuil_securite,
            line_dash='dot',
            line_color='#D97706',
            line_width=1.5,
            annotation_text=f"Seuil de sécurité ({format_dh(st.session_state.seuil_securite)})",
            annotation_position="bottom right",
            annotation_font=dict(color="#D97706", size=10)
        )
        
        # Ligne de référence à 0 DH (Rouge #DC2626)
        fig_evol.add_hline(
            y=0,
            line_color='#DC2626',
            line_width=1.5,
            annotation_text="Ligne de découvert (0 DH)",
            annotation_position="top right",
            annotation_font=dict(color="#DC2626", size=10)
        )
        
        fig_evol.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#17365D", family="Plus Jakarta Sans"),
            height=360,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(
                gridcolor="#E2E8F0",
                linecolor="#DCE5EF",
                tickfont=dict(color="#475569", size=10),
                title="Date de l'opération"
            ),
            yaxis=dict(
                gridcolor="#E2E8F0",
                linecolor="#DCE5EF",
                tickfont=dict(color="#475569", size=10),
                title="Montant (DH)",
                zeroline=False
            ),
            legend=dict(orientation="h", y=1.08, x=0)
        )
        st.plotly_chart(fig_evol, use_container_width=True)
    else:
        st.info("Renseignez un solde initial pour tracer la courbe d'évolution du solde cumulé.")

with col_chart2:
    st.markdown("**Encaissements contre Décaissements**")
    
    # Donut chart de répartition des flux
    fig_comp = go.Figure(data=[go.Pie(
        labels=["Encaissements", "Décaissements"],
        values=[total_encaissements, total_decaissements],
        hole=0.55,
        marker=dict(colors=["#087F8C", "#E11D48"], line=dict(color="#FFFFFF", width=2)),
        textinfo='percent+label',
        hoverinfo='label+value+percent'
    )])
    
    fig_comp.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#17365D", family="Plus Jakarta Sans"),
        height=360,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )
    st.plotly_chart(fig_comp, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 11. SECTION 5 : PRÉVISIONS IA & ANALYSE ET RECOMMANDATIONS (OBJECTIF 5)
# ==============================================================================
st.markdown("""
<div class="content-card">
    <div class="card-title">Prévisions et recommandations</div>
    <div class="card-subtitle">Analyse descriptive des tendances et modélisation prévisionnelle.</div>
""", unsafe_allow_html=True)

# Analyse du niveau d'historique disponible
# Regroupement mensuel des opérations
df_ops_mois = df_ops.copy()
df_ops_mois['Mois_Annee'] = df_ops_mois['Date'].dt.to_period('M')
nb_mois_historique = df_ops_mois['Mois_Annee'].nunique()

tab_recom, tab_ia, tab_synthese = st.tabs([
    "Analyse et recommandations",
    "Modélisation Machine Learning",
    "Synthèse de gestion financière"
])

# ------------------------------------------------------------------------------
# ONGLET 1 : ANALYSE ET RECOMMANDATIONS (ACTIONS CONCRÈTES)
# ------------------------------------------------------------------------------
with tab_recom:
    # 1. Vérification si passage sous zéro ou déficit
    periode_decouvert = False
    if solde_initial is not None:
        min_solde = df_chronologique['Solde_Cumule_DH'].min()
        if min_solde < 0:
            periode_decouvert = True
    else:
        min_solde = None

    # Ratio de couverture
    decaissement_journalier = total_decaissements / max(1, (df_ops['Date'].max() - df_ops['Date'].min()).days) if total_decaissements > 0 else 0
    if solde_final is not None and decaissement_journalier > 0 and solde_final > 0:
        jours_couverture = round(solde_final / decaissement_journalier, 1)
    else:
        jours_couverture = 0.0

    # Diagnostic de situation
    if solde_final is not None and solde_final < 0:
        # ALERTE ROUGE
        deficit = abs(solde_final)
        st.markdown(f"""
        <div class="alert-card alert-danger">
            <div class="alert-heading heading-red">Alerte Risque : Déficit de trésorerie avéré ({format_dh(solde_final)})</div>
            <div class="alert-text">
                Les décaissements totaux de la période ({format_dh(total_decaissements)}) excèdent la somme du solde initial 
                et des encaissements enregistrés ({format_dh((solde_initial or 0) + total_encaissements)}). 
                Le besoin de financement immédiat s'élève à <strong>{format_dh(deficit)}</strong>.
            </div>
            <div class="alert-actions-title">Actions correctives prioritaires :</div>
            <ul class="alert-actions-list">
                <li><strong>Mobilisation rapide des créances :</strong> Sollicitez l'escompte bancaire d'effets de commerce ou le recours à l'affacturage sur les factures clients en attente pour injecter des liquidités.</li>
                <li><strong>Échelonnement négocié des dettes fournisseurs :</strong> Prenez contact avec vos fournisseurs stratégiques pour convenir d'un moratoire ou d'un calendrier d'étalement des règlements.</li>
                <li><strong>Autorisation de découvert préventive :</strong> Sollicitez formellement auprès de votre agence bancaire une facilité de caisse temporaire d'au moins {format_dh(round(deficit * 1.2, -2))}.</li>
                <li><strong>Gel des dépenses non indispensables :</strong> Stoppez immédiatement les engagements d'achats non opérationnels pour préserver le paiement des salaires et charges obligatoires.</li>
            </ul>
            <div class="alert-disclaimer">Aide à la décision : ces orientations constituent des recommandations prudentes de gestion financière.</div>
        </div>
        """, unsafe_allow_html=True)

    elif solde_final is not None and 0 <= solde_final <= st.session_state.seuil_securite:
        # ALERTE ORANGE
        ecart_seuil = st.session_state.seuil_securite - solde_final
        st.markdown(f"""
        <div class="alert-card alert-vigilance">
            <div class="alert-heading heading-orange">Vigilance : Trésorerie positive mais inférieure au seuil ({format_dh(solde_final)})</div>
            <div class="alert-text">
                Le solde final estimé reste positif mais inférieur à votre seuil de sécurité fixé à {format_dh(st.session_state.seuil_securite)} 
                (écart de <strong>{format_dh(ecart_seuil)}</strong>). Votre autonomie financière ne représente qu'environ <strong>{jours_couverture} jours</strong> de décaissements moyens.
            </div>
            <div class="alert-actions-title">Actions préventives recommandées :</div>
            <ul class="alert-actions-list">
                <li><strong>Relance active des créances clients :</strong> Contactez les clients dont les factures approchent de leur échéance pour sécuriser les dates de règlement.</li>
                <li><strong>Surveillance des délais de paiement (DSO) :</strong> Tout retard imprévu de règlement client ferait basculer le compte en découvert bancaire.</li>
                <li><strong>Alignement du calendrier des règlements :</strong> Calez les sorties de fonds vers les fournisseurs après la réception effective des encaissements clients majeurs.</li>
                <li><strong>Arbitrage sur les investissements :</strong> Reportez les achats de matériel ou prestations non prioritaires au mois prochain.</li>
            </ul>
            <div class="alert-disclaimer">Aide à la décision : ces orientations constituent des recommandations prudentes de gestion financière.</div>
        </div>
        """, unsafe_allow_html=True)

    elif solde_final is not None and solde_final > st.session_state.seuil_securite:
        # SITUATION VERTE
        marge = solde_final - st.session_state.seuil_securite
        st.markdown(f"""
        <div class="alert-card alert-favorable">
            <div class="alert-heading heading-turquoise">Situation favorable : Excédent de trésorerie ({format_dh(solde_final)})</div>
            <div class="alert-text">
                Le solde final dépasse confortablement votre seuil de sécurité ({format_dh(st.session_state.seuil_securite)}) 
                avec une réserve excédentaire de <strong>{format_dh(marge)}</strong>. 
                L'autonomie financière couvre environ <strong>{jours_couverture} jours</strong> d'activité normale.
            </div>
            <div class="alert-actions-title">Opportunités d'optimisation financière :</div>
            <ul class="alert-actions-list">
                <li><strong>Placement des liquidités dormantes :</strong> Évaluez l'opportunité de placer une fraction des fonds excédentaires sur des supports sécurisés à court terme (Dépôts à terme ou OPCVM monétaires).</li>
                <li><strong>Escomptes pour paiement comptant :</strong> Négociez avec vos fournisseurs clés un escompte commercial (1 % à 2 %) en échange d'un règlement anticipé.</li>
                <li><strong>Poursuite de la rigueur de recouvrement :</strong> Conservez les procédures de relance préventive pour maintenir cette régularité de cash-flow.</li>
            </ul>
            <div class="alert-disclaimer">Aide à la décision : ces orientations constituent des recommandations prudentes de gestion financière.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Renseignez un solde initial pour générer l'analyse diagnostique complète de trésorerie.")

# ------------------------------------------------------------------------------
# ONGLET 2 : MODÉLISATION MACHINE LEARNING (RIDGE)
# ------------------------------------------------------------------------------
with tab_ia:
    st.markdown("##### Prévisions algorithmiques par Machine Learning")
    
    # Vérification de l'adéquation de l'historique
    if nb_mois_historique < 6:
        st.warning(f"""
        **Historique importé limité ({nb_mois_historique} mois d'activité détecté) :**  
        Un modèle d'apprentissage automatique supervisé (Machine Learning) nécessite au minimum 
        **6 à 12 mois de données continues** pour apprendre rigoureusement les tendances et la saisonnalité 
        sans produire de résultats aléatoires ou trompeurs.
        
        Pour préserver la fiabilité financière, SmartCash AI vous propose ci-dessous une projection analytique basée sur vos flux moyens réels, ou vous permet de tester le modèle complet sur les 24 mois de données d'entreprise disponibles.
        """)
        
        # Projection analytique prudente basée sur les moyennes constatées
        moy_enc_jour = total_encaissements / max(1, (df_ops['Date'].max() - df_ops['Date'].min()).days)
        moy_dec_jour = total_decaissements / max(1, (df_ops['Date'].max() - df_ops['Date'].min()).days)
        
        st.markdown("**Projection analytique des 3 prochains mois (Basée sur le rythme réel constaté) :**")
        proj_data = []
        solde_proj = solde_final if solde_final is not None else 50000.0
        
        for m in range(1, 4):
            enc_m = round(moy_enc_jour * 30, 2)
            dec_m = round(moy_dec_jour * 30, 2)
            net_m = round(enc_m - dec_m, 2)
            solde_fin_m = round(solde_proj + net_m, 2)
            
            proj_data.append({
                "Mois": f"Mois +{m}",
                "Solde début (DH)": format_dh(solde_proj),
                "Encaissements estimés (DH)": format_dh(enc_m),
                "Décaissements estimés (DH)": format_dh(dec_m),
                "Flux net estimé (DH)": format_dh(net_m),
                "Solde fin estimé (DH)": format_dh(solde_fin_m)
            })
            solde_proj = solde_fin_m
            
        st.table(pd.DataFrame(proj_data))
        
    else:
        # Entraînement du modèle réel sur données agrégées
        df_hist_24 = charger_ou_generer_donnees()
        modele_ml = ModelePrevisionTresorerie()
        metrics = modele_ml.entrainer(df_hist_24)
        projections_df = modele_ml.prevoir_mois_suivants(nb_mois=3, solde_initial_depart=(solde_final if solde_final is not None else 50000.0))
        
        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1:
            st.metric("Score de fiabilité R²", f"{metrics['r2_global']:.2%}")
        with c_m2:
            st.metric("Erreur moyenne Encaissements", format_dh(metrics['mae_encaissements_dh']))
        with c_m3:
            st.metric("Erreur moyenne Décaissements", format_dh(metrics['mae_decaissements_dh']))
            
        st.dataframe(
            projections_df[[
                'Libelle_Mois', 'Solde_Initial_DH', 'Total_Encaissements_Prevu_DH',
                'Total_Decaissements_Prevu_DH', 'Flux_Net_Prevu_DH', 'Solde_Final_Prevu_DH'
            ]].style.format({
                'Solde_Initial_DH': lambda x: format_dh(x),
                'Total_Encaissements_Prevu_DH': lambda x: format_dh(x),
                'Total_Decaissements_Prevu_DH': lambda x: format_dh(x),
                'Flux_Net_Prevu_DH': lambda x: format_dh(x),
                'Solde_Final_Prevu_DH': lambda x: format_dh(x)
            }),
            use_container_width=True
        )

# ------------------------------------------------------------------------------
# ONGLET 3 : SYNTHÈSE DE GESTION FINANCIÈRE
# ------------------------------------------------------------------------------
with tab_synthese:
    st.markdown("##### Synthèse académique et ratios de trésorerie")
    col_syn1, col_syn2 = st.columns(2)
    with col_syn1:
        st.markdown("""
        **L'équation fondamentale de trésorerie :**
        $$\\text{Solde Final} = \\text{Solde Initial} + \\text{Encaissements} - \\text{Décaissements}$$
        - Les flux sont enregistrés en **comptabilité de trésorerie** (mouvements effectifs en banque/caisse).
        - La trésorerie nette correspond à l'arbitrage entre le **Fonds de Roulement (FRNG)** et le **Besoin en Fonds de Roulement (BFR)**.
        """)
    with col_syn2:
        st.markdown("""
        **Indicateurs de gestion du cycle d'exploitation :**
        - **DSO (Days Sales Outstanding) :** Délai moyen de recouvrement des clients. Au Maroc, la loi sur les délais de paiement fixe des sanctions en cas de dépassement des 60 à 90 jours.
        - **DPO (Days Payable Outstanding) :** Délai moyen de règlement consenti par vos fournisseurs.
        """)

st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 12. PIED DE PAGE
# ==============================================================================
st.markdown("""
<div class="footer-bar">
    SmartCash AI &bull; Application de gestion et prévision de trésorerie d'entreprise &bull; Casablanca, Maroc &bull; Devise : DH
</div>
""", unsafe_allow_html=True)
