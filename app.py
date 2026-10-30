"""
SmartCash AI - Application Intelligente de Gestion et Prévision de Trésorerie (Maroc 🇲🇦)
Fichier principal : app.py
Thème : Bleu Marine Sombre (#0B1630, #101F3D, #172A4D)
Devise : Dirham Marocain (MAD / DH) - Fuseau horaire : Africa/Casablanca
"""

import os
import io
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Modules internes
import data_manager as dm
from data_manager import format_dh, get_now_morocco, get_today_morocco, TAUX_TVA_MAROC
import financial_calculations as fc
import forecast_model as fm
import report_generator as rg

# ---------------------------------------------------------
# CONFIGURATION DE LA PAGE STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="SmartCash AI Maroc | Trésorerie & IA",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# STYLES CSS PERSONNALISÉS (DESIGN BLEU MARINE FONCÉ)
# ---------------------------------------------------------
DARK_NAVY_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #F1F5F9;
    }

    /* Arrière-plan global bleu marine foncé */
    .stApp {
        background-color: #0B1630 !important;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1350px;
    }

    /* Barre latérale */
    section[data-testid="stSidebar"] {
        background-color: #101F3D !important;
        border-right: 1px solid #1E3A5F;
    }

    /* En-tête de marque */
    .brand-header {
        background: linear-gradient(135deg, #101F3D 0%, #172A4D 50%, #1E3A8A 100%);
        border: 1px solid #23385E;
        padding: 22px 28px;
        border-radius: 12px;
        color: #F1F5F9;
        margin-bottom: 22px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    }
    
    .brand-title {
        font-size: 26px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
        color: #FFFFFF;
    }
    
    .brand-subtitle {
        font-size: 14.5px;
        font-weight: 400;
        color: #93C5FD;
        margin-top: 4px;
        margin-bottom: 0;
    }

    /* Cartes KPI bleu marine */
    .kpi-card {
        background-color: #172A4D;
        border: 1px solid #23385E;
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        transition: transform 0.15s ease, border-color 0.15s ease;
        height: 100%;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #3B82F6;
    }

    .kpi-label {
        font-size: 11.5px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #B7C5DA;
        margin-bottom: 5px;
    }

    .kpi-value {
        font-size: 22px;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.25;
    }

    .kpi-sub {
        font-size: 11.5px;
        margin-top: 5px;
        font-weight: 500;
        color: #94A3B8;
    }

    /* Badges financiers */
    .badge-inflow {
        color: #22C55E;
        background-color: rgba(34, 197, 94, 0.15);
        border: 1px solid rgba(34, 197, 94, 0.3);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 11.5px;
        display: inline-block;
    }

    .badge-outflow {
        color: #EF4444;
        background-color: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 11.5px;
        display: inline-block;
    }

    .badge-late {
        color: #EF4444;
        background-color: rgba(239, 68, 68, 0.2);
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
    }

    .badge-pending {
        color: #F59E0B;
        background-color: rgba(245, 158, 11, 0.2);
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }

    .badge-paid {
        color: #22C55E;
        background-color: rgba(34, 197, 94, 0.2);
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }

    /* Cartes d'alertes */
    .alert-card {
        border-left: 5px solid;
        background-color: #172A4D;
        border-top: 1px solid #23385E;
        border-right: 1px solid #23385E;
        border-bottom: 1px solid #23385E;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }

    .alert-title {
        font-size: 16px;
        font-weight: 700;
        color: #F1F5F9;
        margin-bottom: 4px;
    }

    .alert-body {
        font-size: 13.5px;
        color: #CBD5E1;
        margin-bottom: 6px;
    }

    .alert-recom {
        font-size: 13px;
        color: #93C5FD;
        background-color: rgba(30, 58, 138, 0.35);
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: 500;
    }

    /* Boîte d'information et conteneurs */
    .morocco-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: rgba(30, 58, 138, 0.4);
        border: 1px solid #2563EB;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        color: #BFDBFE;
        font-weight: 600;
    }

    /* Style des formulaires et onglets */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #23385E;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #101F3D;
        border: 1px solid #23385E;
        border-radius: 8px 8px 0 0;
        color: #B7C5DA;
        padding: 8px 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #172A4D !important;
        border-color: #3B82F6 !important;
        color: #FFFFFF !important;
    }

    /* Dataframe et tableaux */
    div[data-testid="stDataFrame"] {
        border: 1px solid #23385E;
        border-radius: 8px;
        background-color: #101F3D;
    }

    /* Inputs et Selects */
    div[data-baseweb="input"], div[data-baseweb="select"] > div {
        background-color: #172A4D !important;
        border-color: #23385E !important;
        color: #F1F5F9 !important;
    }
</style>
"""
st.markdown(DARK_NAVY_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# INITIALISATION ET CHARGEMENT DU SESSION STATE
# ---------------------------------------------------------
if "initial_balance" not in st.session_state:
    st.session_state["initial_balance"] = 120000.0  # 120 000 DH

if "security_threshold" not in st.session_state:
    st.session_state["security_threshold"] = 25000.0  # 25 000 DH

if "transactions_df" not in st.session_state:
    st.session_state["transactions_df"] = dm.load_transactions(st.session_state["initial_balance"])

if "forecast_cache" not in st.session_state:
    st.session_state["forecast_cache"] = None

now_maroc = get_now_morocco()
today_maroc = get_today_morocco()

# ---------------------------------------------------------
# BARRE LATÉRALE DE NAVIGATION ET PARAMÈTRES
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 10px 0 16px 0;">
            <div style="font-size: 32px; margin-bottom: 2px;">🇲🇦 💼</div>
            <div style="font-size: 20px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.3px;">SmartCash AI</div>
            <div style="font-size: 11px; color: #93C5FD; font-weight: 600;">Votre trésorerie, anticipée intelligemment</div>
            <div style="margin-top: 6px;" class="morocco-badge">Devise : Dirham Marocain (MAD)</div>
        </div>
    """, unsafe_allow_html=True)

    menu_choice = st.radio(
        "Navigation principale",
        [
            "📊 Tableau de bord",
            "💳 Opérations & Facturation",
            "📥 Importation de données",
            "🤖 Prévision IA (MAD)",
            "⚠️ Alertes & Recommandations",
            "📈 Analyse & Rapports",
            "🧠 Comprendre l'IA (Module)"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("#### ⚙️ Paramètres de Trésorerie (DH)")

    initial_balance_input = st.number_input(
        "Solde initial de départ (DH)",
        min_value=-500000.0,
        max_value=10000000.0,
        value=float(st.session_state["initial_balance"]),
        step=5000.0,
        format="%.2f",
        help="Solde disponible au début de la période d'analyse en Dirhams marocains."
    )
    if initial_balance_input != st.session_state["initial_balance"]:
        st.session_state["initial_balance"] = initial_balance_input
        st.session_state["forecast_cache"] = None
        st.rerun()

    security_threshold_input = st.number_input(
        "Seuil d'alerte sécurité (DH)",
        min_value=0.0,
        max_value=1000000.0,
        value=float(st.session_state["security_threshold"]),
        step=5000.0,
        format="%.2f",
        help="Matelas de sécurité minimal en DH en dessous duquel une alerte de tension est levée."
    )
    if security_threshold_input != st.session_state["security_threshold"]:
        st.session_state["security_threshold"] = security_threshold_input
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🔄 Données de Démonstration (Maroc)")
    st.caption("Jeu de simulation réaliste : **Atlas Distribution SARL (Casablanca)** sur 5 mois.")

    with st.popover("Recharger la démo marocaine", use_container_width=True):
        st.warning("Cette action rechargera le jeu de données démo marocain complet.")
        if st.button("Confirmer le rechargement démo", type="primary", use_container_width=True):
            st.session_state["transactions_df"] = dm.reset_to_sample_data()
            st.session_state["forecast_cache"] = None
            st.success("Données de démonstration rechargées !")
            st.rerun()

    st.markdown("---")
    st.markdown(f"""
        <div style="font-size: 11px; color: #94A3B8; text-align: center; line-height: 1.4;">
            <strong>SmartCash AI 🇲🇦 v2.0</strong><br>
            Fuseau : <code>Africa/Casablanca</code><br>
            Date : <strong>{now_maroc.strftime('%d/%m/%Y %H:%M')}</strong><br>
            Gestion Financière & Machine Learning
        </div>
    """, unsafe_allow_html=True)


# Données actives
df_current = st.session_state["transactions_df"].copy()
initial_bal = st.session_state["initial_balance"]
sec_thresh = st.session_state["security_threshold"]

# Calcul automatique des prévisions par défaut pour alimenter le tableau de bord et les alertes
if st.session_state["forecast_cache"] is None:
    try:
        st.session_state["forecast_cache"] = fm.train_and_forecast_cashflow(
            df_current,
            initial_balance=initial_bal,
            horizon_days=15,
            model_type="Random Forest (IA)"
        )
    except Exception as e:
        st.session_state["forecast_cache"] = None

forecast_obj = st.session_state["forecast_cache"]
forecast_df = forecast_obj["forecast_df"] if forecast_obj else None

# Calcul des indicateurs et alertes en DH
kpis_global = fc.compute_kpis(df_current, initial_balance=initial_bal, forecast_df=forecast_df)
adv_global = fc.compute_advanced_metrics(df_current, initial_balance=initial_bal)
alerts_global = fc.detect_alerts_and_recommendations(df_current, initial_balance=initial_bal, forecast_df=forecast_df, security_threshold=sec_thresh)


# ==============================================================================
# PAGE 1 : TABLEAU DE BORD (DASHBOARD)
# ==============================================================================
if menu_choice == "📊 Tableau de bord":
    st.markdown("""
        <div class="brand-header">
            <h1 class="brand-title">SmartCash AI 🇲🇦 — Tableau de bord Financier</h1>
            <p class="brand-subtitle">Votre trésorerie, anticipée intelligemment | Contexte Entreprises Maroc (MAD / DH)</p>
        </div>
    """, unsafe_allow_html=True)

    # Filtre de période
    col_f1, col_f2 = st.columns([2, 5])
    with col_f1:
        period_choice = st.selectbox(
            "Période d'analyse :",
            ["Tout l'historique", "30 derniers jours", "60 derniers jours", "90 derniers jours"]
        )

    filtered_df = df_current.copy()
    filtered_df["dt"] = pd.to_datetime(filtered_df["date"])
    max_d = filtered_df["dt"].max() if not filtered_df.empty else pd.to_datetime(today_maroc)

    if period_choice == "30 derniers jours":
        filtered_df = filtered_df[filtered_df["dt"] >= (max_d - timedelta(days=30))]
    elif period_choice == "60 derniers jours":
        filtered_df = filtered_df[filtered_df["dt"] >= (max_d - timedelta(days=60))]
    elif period_choice == "90 derniers jours":
        filtered_df = filtered_df[filtered_df["dt"] >= (max_d - timedelta(days=90))]

    kpis_view = fc.compute_kpis(filtered_df, initial_balance=initial_bal, forecast_df=forecast_df)

    # LIGNE 1 : 4 KPIs de Trésorerie Principaux
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Solde Actuel</div>
                <div class="kpi-value" style="color: {'#FFFFFF' if kpis_view['solde_actuel'] >= 0 else '#EF4444'};">
                    {format_dh(kpis_view['solde_actuel'])}
                </div>
                <div class="kpi-sub">Liquidités en banque</div>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Encaissements</div>
                <div class="kpi-value" style="color: #22C55E;">
                    +{format_dh(kpis_view['total_encaissements'])}
                </div>
                <div class="kpi-sub" style="color: #22C55E;">Recettes & Ventes TTC</div>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Décaissements</div>
                <div class="kpi-value" style="color: #EF4444;">
                    -{format_dh(kpis_view['total_decaissements'])}
                </div>
                <div class="kpi-sub" style="color: #EF4444;">Sorties & Charges TTC</div>
            </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Solde Prévisionnel</div>
                <div class="kpi-value" style="color: {'#3B82F6' if kpis_view['solde_previsionnel'] >= 0 else '#EF4444'};">
                    {format_dh(kpis_view['solde_previsionnel'])}
                </div>
                <div class="kpi-sub" style="color: #93C5FD;">Horizon {forecast_df.shape[0] if forecast_df is not None else 0}j (IA)</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # LIGNE 2 : 4 KPIs de Gestion Marocaine (Créances, Dettes, Paiements à venir, Risque)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Créances Clients (BFR)</div>
                <div class="kpi-value" style="color: #38BDF8;">
                    {format_dh(kpis_view['creances_clients'])}
                </div>
                <div class="kpi-sub" style="color: {'#EF4444' if kpis_view['creances_echues'] > 0 else '#94A3B8'};">
                    Dont échues : {format_dh(kpis_view['creances_echues'])}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Dettes Fournisseurs</div>
                <div class="kpi-value" style="color: #F87171;">
                    {format_dh(kpis_view['dettes_fournisseurs'])}
                </div>
                <div class="kpi-sub" style="color: {'#EF4444' if kpis_view['dettes_echues'] > 0 else '#94A3B8'};">
                    Dont échues : {format_dh(kpis_view['dettes_echues'])}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Paiements à venir (30j)</div>
                <div class="kpi-value" style="color: #FBBF24;">
                    {format_dh(kpis_view['paiements_a_venir'])}
                </div>
                <div class="kpi-sub">Échéances charges & achats</div>
            </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Niveau de Risque</div>
                <div class="kpi-value" style="color: {kpis_view['risque_couleur']};">
                    {kpis_view['niveau_risque']}
                </div>
                <div class="kpi-sub">
                    Variation : {kpis_view['variation_pct']:+.1f}% ({format_dh(kpis_view['variation_valeur'])})
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Diagnostic rédigé en langage financier
    st.info(fc.generate_executive_summary(kpis_view, adv_global, alerts_global))

    # Graphiques Plotly Dark Navy
    daily_hist = fc.compute_daily_cashflow(filtered_df, initial_balance=initial_bal)

    col_g1, col_g2 = st.columns([7, 5])

    with col_g1:
        st.subheader("📈 Trajectoire de Trésorerie (Historique & Prévision en DH)")
        fig_trend = go.Figure()

        # Série historique
        if not daily_hist.empty:
            fig_trend.add_trace(go.Scatter(
                x=daily_hist["date"],
                y=daily_hist["solde_cumule"],
                mode="lines",
                name="Solde Réalisé (DH)",
                line=dict(color="#3B82F6", width=2.8),
                hovertemplate="<b>Date</b>: %{x|%d/%m/%Y}<br><b>Solde</b>: %{y:,.2f} DH<extra></extra>"
            ))

        # Série prévisionnelle IA
        if forecast_df is not None and not forecast_df.empty:
            last_hist_pt = daily_hist.iloc[[-1]] if not daily_hist.empty else pd.DataFrame()
            if not last_hist_pt.empty:
                raccord_x = [last_hist_pt["date"].iloc[0]] + list(forecast_df["date"])
                raccord_y = [last_hist_pt["solde_cumule"].iloc[0]] + list(forecast_df["solde_prevu"])
            else:
                raccord_x = list(forecast_df["date"])
                raccord_y = list(forecast_df["solde_prevu"])

            fig_trend.add_trace(go.Scatter(
                x=raccord_x,
                y=raccord_y,
                mode="lines+markers",
                name="Solde Prévu IA (DH)",
                line=dict(color="#A78BFA", width=2.6, dash="dash"),
                marker=dict(size=4),
                hovertemplate="<b>Date</b>: %{x|%d/%m/%Y}<br><b>Solde prévisionnel</b>: %{y:,.2f} DH<extra></extra>"
            ))

        # Seuil de sécurité
        fig_trend.add_hline(
            y=sec_thresh,
            line_dash="dot",
            line_color="#F59E0B",
            annotation_text=f"Seuil de sécurité ({format_dh(sec_thresh)})",
            annotation_position="bottom right",
            annotation_font_color="#FBBF24"
        )
        
        # Ligne de découvert
        fig_trend.add_hline(
            y=0,
            line_dash="solid",
            line_color="#EF4444",
            annotation_text="Découvert bancaire (0 DH)",
            annotation_position="top left",
            annotation_font_color="#EF4444"
        )

        fig_trend.update_layout(
            height=390,
            margin=dict(l=20, r=20, t=25, b=20),
            paper_bgcolor="#172A4D",
            plot_bgcolor="#0B1630",
            font=dict(color="#F1F5F9"),
            xaxis=dict(gridcolor="#23385E", zerolinecolor="#23385E"),
            yaxis=dict(gridcolor="#23385E", zerolinecolor="#23385E", ticksuffix=" DH"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_g2:
        st.subheader("🥧 Répartition des Charges (PCGE)")
        cat_expenses = adv_global.get("cat_expenses", pd.DataFrame())
        if not cat_expenses.empty:
            fig_pie = px.pie(
                cat_expenses,
                names="categorie",
                values="montant",
                hole=0.45,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate="<b>%{label}</b><br>Montant: %{value:,.2f} DH<br>Part: %{percent}<extra></extra>"
            )
            fig_pie.update_layout(
                height=390,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="#172A4D",
                font=dict(color="#F1F5F9"),
                showlegend=False
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Aucune dépense disponible pour la répartition.")

    # Graphique barres comparatif mensuel des flux
    st.subheader("📊 Comparaison des Flux : Encaissements vs Décaissements (MAD)")
    df_flux = filtered_df.copy()
    df_flux["mois"] = pd.to_datetime(df_flux["date"]).dt.strftime("%Y-%m")
    flux_monthly = df_flux.groupby(["mois", "type"])["montant"].sum().unstack(fill_value=0.0).reset_index()
    if "Encaissement" not in flux_monthly.columns:
        flux_monthly["Encaissement"] = 0.0
    if "Décaissement" not in flux_monthly.columns:
        flux_monthly["Décaissement"] = 0.0

    fig_bars = go.Figure()
    fig_bars.add_trace(go.Bar(
        x=flux_monthly["mois"],
        y=flux_monthly["Encaissement"],
        name="Encaissements (DH)",
        marker_color="#22C55E",
        hovertemplate="<b>%{x}</b><br>Encaissements: %{y:,.2f} DH<extra></extra>"
    ))
    fig_bars.add_trace(go.Bar(
        x=flux_monthly["mois"],
        y=flux_monthly["Décaissement"],
        name="Décaissements (DH)",
        marker_color="#EF4444",
        hovertemplate="<b>%{x}</b><br>Décaissements: %{y:,.2f} DH<extra></extra>"
    ))
    fig_bars.update_layout(
        barmode="group",
        height=320,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="#172A4D",
        plot_bgcolor="#0B1630",
        font=dict(color="#F1F5F9"),
        xaxis=dict(title="Mois", gridcolor="#23385E"),
        yaxis=dict(title="Volume (DH)", gridcolor="#23385E", ticksuffix=" DH"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_bars, use_container_width=True)


# ==============================================================================
# PAGE 2 : GESTION DES OPÉRATIONS & FACTURATION
# ==============================================================================
elif menu_choice == "💳 Opérations & Facturation":
    st.markdown("""
        <div class="brand-header">
            <h1 class="brand-title">Opérations Financières & Facturation (Maroc)</h1>
            <p class="brand-subtitle">Gestion des factures clients/fournisseurs, TVA marocaine (HT, TVA, TTC) et suivi des échéances</p>
        </div>
    """, unsafe_allow_html=True)

    tab_consulter, tab_echeances, tab_ajouter, tab_modifier = st.tabs([
        "📋 Grand Livre des Opérations",
        "📑 Suivi Créances & Dettes (Échéancier)",
        "➕ Enregistrer une Facture / Opération",
        "✏️ Modifier ou Supprimer"
    ])

    # 1. AJOUT D'UNE OPÉRATION
    with tab_ajouter:
        st.subheader("Enregistrer une Facture ou une Opération financière")
        st.caption("Calcul automatique de la TVA marocaine et cohérence HT / TTC.")
        
        with st.form("form_add_morocco_op", clear_on_submit=True):
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                new_date = st.date_input("Date de l'opération", value=today_maroc)
                new_ech = st.date_input("Date d'échéance de paiement", value=today_maroc + timedelta(days=30))
                new_type = st.selectbox("Type d'opération", ["Encaissement", "Décaissement"])
                new_partenaire = st.text_input("Partenaire (Client ou Fournisseur)", placeholder="Ex: OCP Solutions, SNTL, Lydec...")

            with f_col2:
                cat_choices = dm.CATEGORIES_ENCAISSEMENT if new_type == "Encaissement" else dm.CATEGORIES_DECAISSEMENT
                new_cat = st.selectbox("Catégorie (Plan Comptable PCGE)", cat_choices)
                new_libelle = st.text_input("Libellé / Réf Facture", placeholder="Ex: Facture Client #FC-2026-102")
                new_statut = st.selectbox("Statut de réalisation", ["Réalisé", "Prévu"], index=1 if new_ech > today_maroc else 0)

            with f_col3:
                new_taux_tva = st.selectbox("Taux de TVA Maroc (%)", TAUX_TVA_MAROC, index=0, format_func=lambda x: f"{x:.0f}% (CGI Maroc)" if x > 0 else "0% (Exonéré)")
                saisie_mode = st.radio("Saisir par :", ["Montant HT", "Montant TTC"], horizontal=True)
                if saisie_mode == "Montant HT":
                    input_ht = st.number_input("Montant Hors Taxes (DH)", min_value=0.01, max_value=5000000.0, value=25000.0, step=500.0, format="%.2f")
                    calc_tva = round(input_ht * (new_taux_tva / 100.0), 2)
                    calc_ttc = round(input_ht + calc_tva, 2)
                    st.info(f"👉 **TVA :** {format_dh(calc_tva)} | **Total TTC :** {format_dh(calc_ttc)}")
                    final_ht = input_ht
                    final_ttc = calc_ttc
                else:
                    input_ttc = st.number_input("Montant TTC / Trésorerie (DH)", min_value=0.01, max_value=5000000.0, value=30000.0, step=500.0, format="%.2f")
                    calc_ht = round(input_ttc / (1.0 + (new_taux_tva / 100.0)), 2)
                    calc_tva = round(input_ttc - calc_ht, 2)
                    st.info(f"👉 **HT calculé :** {format_dh(calc_ht)} | **TVA :** {format_dh(calc_tva)}")
                    final_ht = calc_ht
                    final_ttc = input_ttc

            new_commentaire = st.text_input("Commentaire / Modalité de règlement", placeholder="Ex: Virement bancaire, chèque barré, traite 60 jours...")

            submit_add = st.form_submit_button("💾 Enregistrer l'opération en Dirhams", type="primary", use_container_width=True)

            if submit_add:
                if not new_libelle.strip():
                    st.error("Veuillez renseigner un libellé ou une référence pour l'opération.")
                else:
                    updated_df = dm.add_transaction(
                        date_op=str(new_date),
                        libelle=new_libelle,
                        type_op=new_type,
                        categorie=new_cat,
                        montant=final_ttc,
                        statut=new_statut,
                        commentaire=new_commentaire,
                        date_echeance=str(new_ech),
                        partenaire=new_partenaire,
                        montant_ht=final_ht,
                        taux_tva=new_taux_tva
                    )
                    st.session_state["transactions_df"] = updated_df
                    st.session_state["forecast_cache"] = None
                    st.success(f"Opération '{new_libelle}' enregistrée avec succès ({format_dh(final_ttc)}) !")
                    st.rerun()

    # 2. CONSULTATION & RECHERCHE
    with tab_consulter:
        fil_c1, fil_c2, fil_c3, fil_c4 = st.columns([3, 2, 2, 2])
        with fil_c1:
            search_query = st.text_input("🔍 Rechercher par libellé, partenaire ou note", "")
        with fil_c2:
            type_filter = st.selectbox("Filtrer par type", ["Tous", "Encaissement", "Décaissement"])
        with fil_c3:
            cat_filter = st.selectbox("Filtrer par catégorie PCGE", ["Toutes"] + dm.ALL_CATEGORIES)
        with fil_c4:
            statut_filter = st.selectbox("Filtrer par statut", ["Tous", "Réalisé", "Prévu"])

        view_df = df_current.copy()

        if search_query.strip():
            q = search_query.lower().strip()
            view_df = view_df[
                view_df["libelle"].astype(str).str.lower().str.contains(q) |
                view_df["partenaire"].astype(str).str.lower().str.contains(q) |
                view_df["commentaire"].astype(str).str.lower().str.contains(q)
            ]
        if type_filter != "Tous":
            view_df = view_df[view_df["type"] == type_filter]
        if cat_filter != "Toutes":
            view_df = view_df[view_df["categorie"] == cat_filter]
        if statut_filter != "Tous":
            view_df = view_df[view_df["statut"] == statut_filter]

        st.caption(f"Affichage de **{len(view_df)}** opération(s) sur **{len(df_current)}** au total.")

        # Affichage avec formatage en Dirhams
        display_df = view_df.copy()
        display_df["Montant HT (DH)"] = display_df["montant_ht"].apply(lambda x: format_dh(x, include_symbol=False))
        display_df["Taux TVA"] = display_df["taux_tva"].apply(lambda x: f"{x:.0f}%")
        display_df["TVA (DH)"] = display_df["montant_tva"].apply(lambda x: format_dh(x, include_symbol=False))
        display_df["Montant TTC (DH)"] = display_df.apply(lambda r: f"{'+' if r['type'] == 'Encaissement' else '-'}{format_dh(r['montant'])}", axis=1)

        cols_to_show = [
            "date", "date_echeance", "libelle", "partenaire", "type",
            "categorie", "Montant HT (DH)", "Taux TVA", "TVA (DH)",
            "Montant TTC (DH)", "statut", "statut_paiement"
        ]
        
        st.dataframe(
            display_df[cols_to_show].rename(columns={
                "date": "Date Op.",
                "date_echeance": "Échéance",
                "libelle": "Libellé / Facture",
                "partenaire": "Partenaire",
                "type": "Type",
                "categorie": "Catégorie PCGE",
                "statut": "Statut",
                "statut_paiement": "Paiement"
            }),
            use_container_width=True,
            height=460
        )

    # 3. SUIVI DES CRÉANCES ET DETTES (ÉCHÉANCIER)
    with tab_echeances:
        st.subheader("📑 Échéancier : Suivi des Créances Clients & Dettes Fournisseurs")
        st.write("Ce tableau isole les opérations prévues non encore dénouées pour un pilotage strict du BFR.")

        col_ec1, col_ec2 = st.columns(2)
        
        # Créances clients
        with col_ec1:
            st.markdown("#### 🟢 Créances Clients à Recouvrer")
            cr_df = df_current[(df_current["type"] == "Encaissement") & (df_current["statut"] == "Prévu")].copy()
            if not cr_df.empty:
                cr_df["TTC (DH)"] = cr_df["montant"].apply(format_dh)
                st.dataframe(
                    cr_df[["date_echeance", "partenaire", "libelle", "TTC (DH)", "statut_paiement"]].rename(columns={
                        "date_echeance": "Échéance", "partenaire": "Client", "libelle": "Facture", "statut_paiement": "État"
                    }),
                    use_container_width=True
                )
            else:
                st.info("Aucune créance client en attente.")

        # Dettes fournisseurs
        with col_ec2:
            st.markdown("#### 🔴 Dettes Fournisseurs à Régler")
            det_df = df_current[(df_current["type"] == "Décaissement") & (df_current["statut"] == "Prévu")].copy()
            if not det_df.empty:
                det_df["TTC (DH)"] = det_df["montant"].apply(format_dh)
                st.dataframe(
                    det_df[["date_echeance", "partenaire", "libelle", "TTC (DH)", "statut_paiement"]].rename(columns={
                        "date_echeance": "Échéance", "partenaire": "Fournisseur", "libelle": "Facture", "statut_paiement": "État"
                    }),
                    use_container_width=True
                )
            else:
                st.info("Aucune dette fournisseur en attente.")

    # 4. MODIFIER OU SUPPRIMER
    with tab_modifier:
        st.subheader("Modifier ou Supprimer une opération")
        if df_current.empty:
            st.info("Aucune opération à modifier.")
        else:
            op_dict = {
                f"{row['date']} | {row['type']} | {row.get('partenaire', 'Divers')} : {row['libelle']} ({format_dh(row['montant'])}) [ID:{row['id']}]": row["id"]
                for _, row in df_current.iterrows()
            }
            sel_label = st.selectbox("Sélectionnez l'opération à traiter :", list(op_dict.keys()))
            sel_id = op_dict[sel_label]
            row_data = df_current[df_current["id"] == sel_id].iloc[0]

            with st.form("form_edit_morocco_op"):
                me_col1, me_col2 = st.columns(2)
                with me_col1:
                    e_date = st.date_input("Date", value=datetime.strptime(row_data["date"], "%Y-%m-%d").date())
                    e_ech = st.date_input("Échéance", value=datetime.strptime(str(row_data.get("date_echeance", row_data["date"])), "%Y-%m-%d").date())
                    e_lib = st.text_input("Libellé", value=row_data["libelle"])
                    e_part = st.text_input("Partenaire", value=str(row_data.get("partenaire", "Divers")))
                    e_type = st.selectbox("Type", ["Encaissement", "Décaissement"], index=0 if row_data["type"] == "Encaissement" else 1)

                with me_col2:
                    current_cat = row_data["categorie"]
                    cat_opts = dm.ALL_CATEGORIES
                    c_idx = cat_opts.index(current_cat) if current_cat in cat_opts else 0
                    e_cat = st.selectbox("Catégorie PCGE", cat_opts, index=c_idx)
                    
                    e_taux = st.selectbox("Taux de TVA (%)", TAUX_TVA_MAROC, index=TAUX_TVA_MAROC.index(float(row_data.get("taux_tva", 20.0))) if float(row_data.get("taux_tva", 20.0)) in TAUX_TVA_MAROC else 0)
                    e_ttc = st.number_input("Montant TTC (DH)", min_value=0.01, value=float(row_data["montant"]), step=100.0, format="%.2f")
                    e_statut = st.selectbox("Statut", ["Réalisé", "Prévu"], index=0 if row_data["statut"] == "Réalisé" else 1)
                    e_comm = st.text_input("Commentaire", value=str(row_data.get("commentaire", "")))

                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    submit_mod = st.form_submit_button("💾 Mettre à jour l'opération", type="primary", use_container_width=True)
                with b_col2:
                    submit_del = st.form_submit_button("🗑️ Supprimer cette opération", use_container_width=True)

                if submit_mod:
                    calc_ht = round(e_ttc / (1.0 + (e_taux / 100.0)), 2)
                    updated_df = dm.update_transaction(
                        op_id=sel_id,
                        date_op=str(e_date),
                        libelle=e_lib,
                        type_op=e_type,
                        categorie=e_cat,
                        montant=e_ttc,
                        statut=e_statut,
                        commentaire=e_comm,
                        date_echeance=str(e_ech),
                        partenaire=e_part,
                        montant_ht=calc_ht,
                        taux_tva=e_taux
                    )
                    st.session_state["transactions_df"] = updated_df
                    st.session_state["forecast_cache"] = None
                    st.success("Opération modifiée avec succès !")
                    st.rerun()

                if submit_del:
                    updated_df = dm.delete_transaction(sel_id)
                    st.session_state["transactions_df"] = updated_df
                    st.session_state["forecast_cache"] = None
                    st.warning("Opération supprimée.")
                    st.rerun()


# ==============================================================================
# PAGE 3 : IMPORTATION DES DONNÉES
# ==============================================================================
elif menu_choice == "📥 Importation de données":
    st.markdown("""
        <div class="brand-header">
            <h1 class="brand-title">Importation des Données Financières (Maroc)</h1>
            <p class="brand-subtitle">Intégrez vos fichiers Excel (.xlsx) ou CSV avec reconnaissance des champs HT, TVA, TTC et Échéances</p>
        </div>
    """, unsafe_allow_html=True)

    col_imp1, col_imp2 = st.columns([5, 3])

    with col_imp2:
        st.markdown("### 📥 Modèles téléchargeables (Maroc)")
        st.write("Téléchargez un modèle pré-configuré avec les colonnes attendues et la TVA marocaine :")
        
        if os.path.exists(dm.TEMPLATE_CSV):
            with open(dm.TEMPLATE_CSV, "rb") as f_csv:
                st.download_button(
                    label="📄 Télécharger le Modèle CSV (DH)",
                    data=f_csv,
                    file_name="modele_smartcash_maroc.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        if os.path.exists(dm.TEMPLATE_XLSX):
            with open(dm.TEMPLATE_XLSX, "rb") as f_xlsx:
                st.download_button(
                    label="📊 Télécharger le Modèle Excel (.xlsx)",
                    data=f_xlsx,
                    file_name="modele_smartcash_maroc.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

        st.markdown("""
            <div style="background-color: #172A4D; border: 1px solid #23385E; border-radius: 8px; padding: 14px; margin-top: 15px; font-size: 13px;">
                <strong>Colonnes prises en charge :</strong>
                <ul>
                    <li><code>Date</code> (Date de facturation / opération)</li>
                    <li><code>Date Échéance</code> (Date limite de paiement)</li>
                    <li><code>Libellé</code> & <code>Partenaire</code> (Client ou Fournisseur)</li>
                    <li><code>Type</code> (Encaissement ou Décaissement)</li>
                    <li><code>Montant HT</code> & <code>Taux TVA</code> (ex: 20%, 14%, 10%, 7%, 0%)</li>
                    <li><code>Montant TTC</code> (ou montant total en DH)</li>
                    <li><code>Statut</code> (Réalisé ou Prévu)</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    with col_imp1:
        st.markdown("### 📤 Téléverser un fichier financier")
        uploaded_file = st.file_uploader(
            "Sélectionnez votre fichier Excel (.xlsx, .xls) ou CSV (.csv)",
            type=["csv", "xlsx", "xls"]
        )

        if uploaded_file is not None:
            with st.spinner("Analyse et validation de conformité marocaine en cours..."):
                valid_df, errors, duplicates = dm.parse_and_validate_import(
                    uploaded_file, uploaded_file.name
                )

            if errors:
                st.error("Des anomalies ont été détectées lors de l'analyse :")
                for err in errors[:5]:
                    st.write(f"- ⚠️ {err}")
                if len(errors) > 5:
                    st.caption(f"... et {len(errors) - 5} autre(s) erreur(s).")

            if valid_df is not None and not valid_df.empty:
                st.success(f"✅ **{len(valid_df)} opération(s) valide(s)** détectée(s) !")
                if duplicates > 0:
                    st.warning(f"ℹ️ {duplicates} doublon(s) potentiel(s) détecté(s).")

                st.markdown("#### Aperçu des données à intégrer (Montants en DH) :")
                preview_show = valid_df.copy()
                preview_show["TTC (DH)"] = preview_show["montant"].apply(format_dh)
                st.dataframe(
                    preview_show[["date", "date_echeance", "libelle", "partenaire", "type", "TTC (DH)", "statut"]].head(8),
                    use_container_width=True
                )

                st.markdown("---")
                mode_import = st.radio(
                    "Mode d'intégration :",
                    ["Fusionner avec les données existantes (Conserve l'historique)", "Remplacer entièrement les données existantes"]
                )

                if st.button("🚀 Confirmer l'intégration dans SmartCash AI", type="primary", use_container_width=True):
                    if "Fusionner" in mode_import:
                        final_df = pd.concat([st.session_state["transactions_df"], valid_df], ignore_index=True)
                    else:
                        final_df = valid_df

                    final_df = final_df.sort_values(by=["date", "type"], ascending=[True, False]).reset_index(drop=True)
                    dm.save_transactions(final_df)
                    st.session_state["transactions_df"] = final_df
                    st.session_state["forecast_cache"] = None
                    st.success(f"🎉 {len(valid_df)} opérations importées avec succès !")
                    st.rerun()


# ==============================================================================
# PAGE 4 : PRÉVISION INTELLIGENTE PAR IA (MAD)
# ==============================================================================
elif menu_choice == "🤖 Prévision IA (MAD)":
    st.markdown("""
        <div class="brand-header">
            <h1 class="brand-title">Moteur de Prévision Intelligente par IA (MAD)</h1>
            <p class="brand-subtitle">Modélisation temporelle et prédiction du solde de trésorerie en Dirhams Marocains</p>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("⚙️ Configuration du modèle prédictif")
    col_fc1, col_fc2, col_fc3 = st.columns(3)
    with col_fc1:
        horizon_choice = st.selectbox("Horizon de projection", [7, 15, 30], index=1, format_func=lambda x: f"{x} jours")
    with col_fc2:
        model_choice = st.selectbox("Algorithme d'apprentissage", ["Random Forest (IA)", "Régression Ridge (Linéaire régularisé)"])
    with col_fc3:
        btn_recalc = st.button("🔄 Entraîner & Projeter la trésorerie", type="primary", use_container_width=True)

    if btn_recalc or st.session_state["forecast_cache"] is None:
        with st.spinner("Entraînement du modèle sur les séries temporelles marocaines..."):
            st.session_state["forecast_cache"] = fm.train_and_forecast_cashflow(
                df_current,
                initial_balance=initial_bal,
                horizon_days=horizon_choice,
                model_type=model_choice
            )

    res = st.session_state["forecast_cache"]

    if res is None:
        st.error("Données insuffisantes pour générer une prévision. Veuillez saisir ou importer des opérations.")
    else:
        fc_df = res["forecast_df"]
        eval_metrics = res["evaluation"]
        model_info = res["model_info"]
        is_fallback = res["is_fallback"]

        if is_fallback:
            st.warning(f"⚠️ **Information méthodologique :** {eval_metrics.get('reason')}")
        else:
            st.success(f"✅ Modèle entraîné : **{model_info['name']}** sur l'historique réalisé.")

        # Graphique principal Plotly Dark
        st.markdown("### 📊 Trajectoire Prévisionnelle & Bornes d'Incertitude (DH)")
        daily_hist = fc.compute_daily_cashflow(df_current[df_current["statut"] == "Réalisé"], initial_balance=initial_bal)

        fig_pred = go.Figure()

        if not daily_hist.empty:
            fig_pred.add_trace(go.Scatter(
                x=daily_hist["date"],
                y=daily_hist["solde_cumule"],
                mode="lines",
                name="Historique Réalisé (DH)",
                line=dict(color="#3B82F6", width=2.8)
            ))

        # Intervalle de confiance
        fig_pred.add_trace(go.Scatter(
            x=list(fc_df["date"]) + list(fc_df["date"])[::-1],
            y=list(fc_df["borne_sup"]) + list(fc_df["borne_inf"])[::-1],
            fill='toself',
            fillcolor='rgba(167, 139, 250, 0.18)',
            line=dict(color='rgba(255,255,255,0)'),
            name="Intervalle d'Incertitude (80%)",
            showlegend=True
        ))

        # Prévision médiane
        last_hist_row = daily_hist.iloc[[-1]] if not daily_hist.empty else pd.DataFrame()
        if not last_hist_row.empty:
            rx = [last_hist_row["date"].iloc[0]] + list(fc_df["date"])
            ry = [last_hist_row["solde_cumule"].iloc[0]] + list(fc_df["solde_prevu"])
        else:
            rx = list(fc_df["date"])
            ry = list(fc_df["solde_prevu"])

        fig_pred.add_trace(go.Scatter(
            x=rx,
            y=ry,
            mode="lines+markers",
            name="Prévision Solde IA (DH)",
            line=dict(color="#A78BFA", width=3, dash="dash"),
            marker=dict(size=4)
        ))

        fig_pred.add_hline(y=sec_thresh, line_dash="dot", line_color="#F59E0B", annotation_text=f"Seuil de sécurité ({format_dh(sec_thresh)})", annotation_font_color="#FBBF24")
        fig_pred.add_hline(y=0, line_dash="solid", line_color="#EF4444", annotation_text="Découvert (0 DH)", annotation_font_color="#EF4444")

        fig_pred.update_layout(
            height=420,
            margin=dict(l=20, r=20, t=25, b=20),
            paper_bgcolor="#172A4D",
            plot_bgcolor="#0B1630",
            font=dict(color="#F1F5F9"),
            xaxis=dict(gridcolor="#23385E"),
            yaxis=dict(gridcolor="#23385E", ticksuffix=" DH"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_pred, use_container_width=True)

        # Métriques d'évaluation réelles en DH
        st.markdown("### 🎯 Métriques Réelles d'Évaluation (Test Set)")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)

        with col_m1:
            mae_val = eval_metrics.get("mae")
            st.metric("Erreur Absolue (MAE)", format_dh(mae_val) if mae_val is not None else "N/A", help="Écart moyen en Dirhams entre le flux réel et la prédiction.")
        with col_m2:
            rmse_val = eval_metrics.get("rmse")
            st.metric("Erreur Quadratique (RMSE)", format_dh(rmse_val) if rmse_val is not None else "N/A", help="Pénalise les gros écarts inattendus en DH.")
        with col_m3:
            r2_val = eval_metrics.get("r2")
            st.metric("Score de Détermination R²", f"{r2_val:.3f}" if r2_val is not None else "N/A", help="Part de la variance expliquée par le modèle.")
        with col_m4:
            st.metric("Échantillon Train / Test", f"{eval_metrics.get('train_size', 0)}j / {eval_metrics.get('test_size', 0)}j")

        # Importance des variables
        importance_dict = model_info.get("importance", {})
        if importance_dict:
            st.markdown("#### 🧠 Facteurs d'Influence Détectés par l'IA :")
            trad_features = {
                "day_of_week": "Jour de la semaine (rythme hebdo Maroc)",
                "day_of_month": "Jour du mois (échéance TVA 20e, paie 28e, loyer 1er)",
                "month": "Saisonnalité mensuelle",
                "is_weekend": "Indicateur Samedi/Dimanche",
                "dow_sin": "Composante cyclique hebdo (sin)",
                "dow_cos": "Composante cyclique hebdo (cos)",
                "dom_sin": "Composante cyclique mensuelle (sin)",
                "dom_cos": "Composante cyclique mensuelle (cos)",
                "lag_1": "Flux de la veille (J-1)",
                "lag_2": "Flux à J-2",
                "lag_7": "Flux du même jour semaine précédente (J-7)",
                "rolling_mean_7": "Moyenne mobile 7 jours",
                "rolling_std_7": "Volatilité des flux 7 jours"
            }
            imp_df = pd.DataFrame(list(importance_dict.items()), columns=["Variable", "Importance"]).sort_values(by="Importance", ascending=True)
            imp_df["Variable"] = imp_df["Variable"].map(lambda x: trad_features.get(x, x))

            fig_imp = px.bar(
                imp_df,
                x="Importance",
                y="Variable",
                orientation="h",
                color="Importance",
                color_continuous_scale="Blues"
            )
            fig_imp.update_layout(
                height=320,
                margin=dict(l=20, r=20, t=10, b=10),
                paper_bgcolor="#172A4D",
                plot_bgcolor="#0B1630",
                font=dict(color="#F1F5F9"),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_imp, use_container_width=True)

        with st.expander("🔍 Tableau détaillé des prévisions journalières (MAD)"):
            disp_fc = fc_df.copy()
            disp_fc["Flux Prévu (DH)"] = disp_fc["flux_prevu"].apply(format_dh)
            disp_fc["Solde Prévu (DH)"] = disp_fc["solde_prevu"].apply(format_dh)
            disp_fc["Borne Inf (DH)"] = disp_fc["borne_inf"].apply(format_dh)
            disp_fc["Borne Sup (DH)"] = disp_fc["borne_sup"].apply(format_dh)
            st.dataframe(disp_fc[["date_str", "Flux Prévu (DH)", "Solde Prévu (DH)", "Borne Inf (DH)", "Borne Sup (DH)"]].rename(columns={"date_str": "Date"}), use_container_width=True)


# ==============================================================================
# PAGE 5 : ALERTES ET RECOMMANDATIONS (MAROC)
# ==============================================================================
elif menu_choice == "⚠️ Alertes & Recommandations":
    st.markdown("""
        <div class="brand-header">
            <h1 class="brand-title">Alertes & Recommandations Managériales 🇲🇦</h1>
            <p class="brand-subtitle">Détection précoce des tensions de liquidités et plans d'action adaptés au contexte économique marocain</p>
        </div>
    """, unsafe_allow_html=True)

    col_flt1, col_flt2 = st.columns([3, 1])
    with col_flt1:
        st.write("Analyse automatique combinant soldes réels, échéances de créances/dettes et prédictions du modèle.")
    with col_flt2:
        filter_grav = st.selectbox("Filtrer par gravité :", ["Toutes", "Critique", "Élevé", "Modéré", "Info"])

    displayed_alerts = alerts_global
    if filter_grav != "Toutes":
        displayed_alerts = [a for a in displayed_alerts if a["gravite"] == filter_grav]

    if not displayed_alerts:
        st.success("✅ Aucune alerte correspondant aux critères de sélection.")
    else:
        for alert in displayed_alerts:
            grav = alert["gravite"]
            col_bar = alert["couleur"]
            st.markdown(f"""
                <div class="alert-card" style="border-left-color: {col_bar};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span class="alert-title">{alert['titre']}</span>
                        <span style="background-color: {col_bar}25; color: {col_bar}; border: 1px solid {col_bar}50; padding: 3px 10px; border-radius: 6px; font-weight: 700; font-size: 11px;">
                            {grav.upper()}
                        </span>
                    </div>
                    <div style="font-size: 12px; color: #94A3B8; margin-bottom: 8px;">
                        <strong>Échéance concernée :</strong> {alert['date']}
                    </div>
                    <div class="alert-body">
                        <strong>Constat chiffré :</strong> {alert['raison']}
                    </div>
                    <div class="alert-recom">
                        💡 <strong>Recommandation managériale :</strong> {alert['recommandation']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 Guide Pratique de Financement Court Terme au Maroc")
    st.markdown("""
    1. **Facilité de caisse / Découvert autorisé :** Négociation d'une autorisation auprès de votre banque marocaine (Attijariwafa, BCP, BOA, CIH, SGMB) pour couvrir les décalages de paie ou de TVA.
    2. **Escompte d'effets de commerce (Traites) :** Mobilisation immédiate en liquidités des lettres de change tirées sur des clients grands comptes.
    3. **Affacturage (Factoring marocain) :** Cession des factures clients avec garantie contre le risque d'impayé (ex: Maroc Factoring, Attijari Factoring).
    4. **Déclarations fiscales DGI & Cotisations CNSS :** Respecter scrupuleusement le calendrier (TVA avant le 20, CNSS avant le 10) pour éviter les pénalités et majorations de retard.
    """)


# ==============================================================================
# PAGE 6 : ANALYSE ET RAPPORTS
# ==============================================================================
elif menu_choice == "📈 Analyse & Rapports":
    st.markdown("""
        <div class="brand-header">
            <h1 class="brand-title">Analyse Financière & Rapports Exécutifs (DH)</h1>
            <p class="brand-subtitle">Position fiscale de TVA marocaine, ratios de gestion et édition de rapports PDF officiels</p>
        </div>
    """, unsafe_allow_html=True)

    # 4 Cartes de ratios financiers en DH
    rc1, rc2, rc3, rc4 = st.columns(4)
    with rc1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Dépense Journalière Moyenne</div>
                <div class="kpi-value">{format_dh(adv_global.get('avg_daily_burn', 0))}</div>
                <div class="kpi-sub">Burn Rate quotidien</div>
            </div>
        """, unsafe_allow_html=True)

    with rc2:
        runway_val = adv_global.get('runway_days', 0)
        runway_color = "#22C55E" if runway_val >= 60 else ("#F59E0B" if runway_val >= 30 else "#EF4444")
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Autonomie Financière</div>
                <div class="kpi-value" style="color: {runway_color};">{runway_val} jours</div>
                <div class="kpi-sub">Runway sans nouvelle recette</div>
            </div>
        """, unsafe_allow_html=True)

    with rc3:
        cov_val = adv_global.get('coverage_ratio', 1.0)
        cov_color = "#22C55E" if cov_val >= 1.10 else ("#F59E0B" if cov_val >= 1.0 else "#EF4444")
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Ratio de Couverture</div>
                <div class="kpi-value" style="color: {cov_color};">{cov_val:.2f}</div>
                <div class="kpi-sub">Recettes / Dépenses (cible > 1.10)</div>
            </div>
        """, unsafe_allow_html=True)

    with rc4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">TVA Nette Due à la DGI</div>
                <div class="kpi-value" style="color: #F87171;">{format_dh(kpis_global.get('tva_due', 0))}</div>
                <div class="kpi-sub">TVA Collectée - Déductible</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Répartition des charges et encaissements en DH
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("🔴 Top 5 des Postes de Décaissements (PCGE)")
        cat_exp = adv_global.get("cat_expenses", pd.DataFrame())
        if not cat_exp.empty:
            cat_exp_disp = cat_exp.head(5).copy()
            cat_exp_disp["Total (DH)"] = cat_exp_disp["montant"].apply(format_dh)
            st.dataframe(
                cat_exp_disp[["categorie", "Total (DH)", "pct"]].rename(columns={"categorie": "Catégorie PCGE", "pct": "Part (%)"}),
                use_container_width=True
            )
        else:
            st.info("Aucun décaissement enregistré.")

    with col_t2:
        st.subheader("🟢 Top des Postes d'Encaissements (PCGE)")
        cat_inf = adv_global.get("cat_inflows", pd.DataFrame())
        if not cat_inf.empty:
            cat_inf_disp = cat_inf.copy()
            cat_inf_disp["Total (DH)"] = cat_inf_disp["montant"].apply(format_dh)
            st.dataframe(
                cat_inf_disp[["categorie", "Total (DH)", "pct"]].rename(columns={"categorie": "Catégorie PCGE", "pct": "Part (%)"}),
                use_container_width=True
            )
        else:
            st.info("Aucun encaissement enregistré.")

    st.markdown("---")
    st.subheader("📄 Exportation du Rapport Exécutif & Données")
    st.write("Générez les documents officiels pour votre direction financière, votre banquier ou votre soutenance :")

    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        st.markdown("#### 📑 Rapport Exécutif PDF Officiel (DH)")
        st.caption("Synthèse financière certifiée SmartCash AI Maroc : KPIs en DH, TVA DGI, BFR et diagnostic IA.")
        
        try:
            pdf_bytes = rg.generate_pdf_report(
                kpis=kpis_global,
                adv=adv_global,
                alerts=alerts_global,
                forecast_data=forecast_obj
            )
            st.download_button(
                label="📥 Télécharger le Rapport PDF en Dirhams",
                data=pdf_bytes,
                file_name=f"Rapport_SmartCash_AI_Maroc_{today_maroc.strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erreur lors de la génération du PDF : {e}")

    with col_exp2:
        st.markdown("#### 📊 Exportation des Données au Format CSV")
        st.caption("Grand livre complet incluant HT, taux de TVA, TVA, TTC, échéances et partenaires.")
        csv_data = df_current.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 Télécharger les Données en CSV",
            data=csv_data,
            file_name=f"Transactions_SmartCash_Maroc_{today_maroc.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )


# ==============================================================================
# PAGE 7 : COMPRENDRE L'IA (MODULE PÉDAGOGIQUE)
# ==============================================================================
elif menu_choice == "🧠 Comprendre l'IA (Module)":
    st.markdown("""
        <div class="brand-header">
            <h1 class="brand-title">Approche Pédagogique : L'IA en Gestion Financière</h1>
            <p class="brand-subtitle">Support académique pour le module Intelligence Artificielle & Soutenance d'examen</p>
        </div>
    """, unsafe_allow_html=True)

    tab_p1, tab_p2, tab_p3, tab_p4, tab_p5 = st.tabs([
        "1. Automatisation vs IA",
        "2. Fonctionnement du Machine Learning",
        "3. Machine Learning vs Deep Learning",
        "4. Feature Engineering Financier",
        "🎤 Guide de Soutenance (5 min)"
    ])

    with tab_p1:
        st.markdown("""
        ### 🔄 Différence fondamentale : Automatisation classique vs Intelligence Artificielle

        Dans un logiciel comptable ou un tableur Excel, les opérations reposent sur des **règles rigides programmées manuellement** :
        - *« SI le solde < 0 ALORS afficher Alerte »*
        - *« Solde fin de mois = Solde début + Somme des flux prévus »*

        #### Pourquoi l'automatisation classique a ses limites en trésorerie ?
        L'entreprise vit dans un écosystème dynamique où les clients ne paient pas tous au même rythme, où l'activité présente des creux le week-end, et où certaines charges se reproduisent selon des motifs périodiques subtils (ex: échéances fiscales du 20 au Maroc, salaires du 28).

        #### L'apport de l'Intelligence Artificielle (Machine Learning) :
        Au lieu de coder manuellement chaque règle, nous fournissons à l'algorithme un **historique d'opérations financières en DH**. Le modèle détecte lui-même les tendances cachées, les saisonnalités calendaires et les corrélations temporelles pour estimer le flux net journalier futur.
        """)

        st.markdown("""
        | Critère | Automatisation Classique (Règles) | Intelligence Artificielle (Machine Learning) |
        | :--- | :--- | :--- |
        | **Origine de la logique** | Conçue manuellement par un développeur | Apprise automatiquement à partir des données passées |
        | **Capacité d'adaptation** | Rigide, plante si un cas imprévu survient | Flexible, s'adapte lorsque de nouvelles données arrivent |
        | **Rôle dans SmartCash AI** | Calcul exact du solde cumulé, seuils d'alerte, TVA | Modélisation statistique du flux net quotidien futur |
        """)

    with tab_p2:
        st.markdown("""
        ### 🤖 Le Fonctionnement Général du Machine Learning Supervisé

        Dans **SmartCash AI**, la prévision de trésorerie est modélisée comme un problème de **Régression Supervisée** :

        1. **La variable cible ($y$) :** Le flux financier net journalier en Dirhams ($\text{Encaissements} - \text{Décaissements}$).
        2. **La matrice des variables explicatives ($X$) :** Les caractéristiques temporelles créées par nos soins (Feature Engineering).
        3. **L'apprentissage (Entraînement) :** L'algorithme (*Random Forest* ou *Ridge*) ajuste ses paramètres internes afin de minimiser l'écart entre sa prédiction et la réalité historique.
        4. **L'évaluation sans triche (Test Set) :** Le modèle est évalué sur les 14 derniers jours d'historique qu'il n'a jamais vus pendant son entraînement. On mesure ainsi des métriques réelles en DH :
           - **MAE (Mean Absolute Error) :** Erreur moyenne absolue en Dirhams.
           - **RMSE :** Sensibilité aux gros écarts inattendus.
           - **R² :** Capacité d'explication de la variance.
        """)

    with tab_p3:
        st.markdown("""
        ### ⚖️ Machine Learning vs Deep Learning : Pourquoi ce choix rigoureux ?

        > **Règle d'honnêteté scientifique :** SmartCash AI utilise des modèles de **Machine Learning tabulaire** (Scikit-learn), et **non du Deep Learning**.

        #### Quand utiliser le Machine Learning (Random Forest, Ridge) ?
        - Idéal pour les données tabulaires de gestion de PME.
        - Fonctionne parfaitement même avec un volume modéré de données (quelques mois à quelques années).
        - Rapide à entraîner, explicable et robuste face au surapprentissage (*overfitting*).

        #### Quand le Deep Learning (LSTM, Transformers) est-il justifié ?
        - Lorsque l'on dispose de centaines de milliers de transactions à haute fréquence (trading de banque d'investissement, big data retail).
        - Pour des flux de données non structurés (vision par ordinateur, traitement du langage naturel, audio).
        - **Inconvénient en trésorerie de PME :** Nécessite des volumes massifs de données, agit comme une "boîte noire" difficile à auditer pour un expert-comptable, et risque d'overfitter sévèrement sur un historique restreint.
        """)

    with tab_p4:
        st.markdown("""
        ### 🛠️ L'Art du Feature Engineering Financier Adapté au Maroc

        En finance, donner une date brute (`2026-10-30`) à un algorithme ne sert à rien. Il faut convertir le temps en variables mathématiques porteuses de sens :

        1. **Encodage cyclique des jours de la semaine :**
           $$\text{dow\_sin} = \sin\left(\frac{2\pi \times \text{jour}}{7}\right), \quad \text{dow\_cos} = \cos\left(\frac{2\pi \times \text{jour}}{7}\right)$$
        2. **Échéances comptables marocaines clés :**
           Le 1er du mois (loyers), le 10 (déclarations CNSS/AMO), le 20 (déclaration TVA DGI), le 28 (salaires).
        3. **Variables décalées (Lags) :**
           Le flux à $J-1$, $J-2$ et surtout à $J-7$ (rappel du même jour de la semaine précédente).
        4. **Statistiques glissantes :**
           La moyenne et la volatilité sur 7 jours pour donner le contexte récent.
        5. **Prise en compte des opérations planifiées :**
           Les charges fixes futures déjà connues sont fusionnées avec la prédiction statistique.
        """)

    with tab_p5:
        st.markdown("""
        ### 🎤 Script recommandé pour votre Soutenance Orale (5 minutes chrono)

        Voici la trame idéale pour captiver votre professeur et vos camarades lors de la démonstration :

        - **Minute 1 — Contexte et Problématique financière marocaine :**
          *« Bonjour. La trésorerie est le nerf de la guerre des entreprises marocaines. Avec des délais de paiement inter-entreprises parfois longs, anticiper les tensions de liquidités est vital. SmartCash AI combine la rigueur comptable du PCGE marocain et le Machine Learning pour anticiper ces ruptures. »*

        - **Minute 2 — Tableau de bord & KPIs en Dirhams :**
          *(Montrez la page Tableau de bord)*  
          *« Dès l'ouverture, le dirigeant visualise son solde actuel en DH, son solde prévisionnel, ses créances clients, ses dettes fournisseurs et son niveau de risque calculé en temps réel. »*

        - **Minute 3 — Démonstration de l'IA et de l'Évaluation :**
          *(Allez sur la page Prévision IA)*  
          *« Nous avons entraîné un algorithme de Random Forest via Scikit-learn. Le modèle intègre les cycles hebdomadaires et les échéances fiscales marocaines. Les performances sont mesurées sur un échantillon test réel avec la MAE en DH et le R². »*

        - **Minute 4 — Alertes managériales & Gestion du BFR :**
          *(Allez sur Alertes & Recommandations puis Opérations)*  
          *« L'IA détecte à l'avance les tensions et propose des solutions concrètes : mobilisation d'effets de commerce, recours à la facilité de caisse bancaire ou relance des créances échues. »*

        - **Minute 5 — Export officiel & Conclusion :**
          *(Allez sur Analyse & Rapports, téléchargez le PDF en DH)*  
          *« En un clic, nous générons un rapport PDF officiel certifié en Dirhams pour le banquier ou le conseil d'administration. Je vous remercie et réponds à vos questions. »*
        """)
