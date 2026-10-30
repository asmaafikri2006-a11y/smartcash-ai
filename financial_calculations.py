"""
SmartCash AI - Calculs Financiers et Détection des Risques (Contexte Marocain 🇲🇦)
Module financial_calculations.py
Effectue les calculs de soldes cumulés en DH/MAD, suivi des créances clients & dettes fournisseurs,
position de TVA marocaine, indicateurs de BFR et alertes managériales contextualisées.
"""

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from data_manager import format_dh, get_today_morocco

def compute_daily_cashflow(df: pd.DataFrame, initial_balance: float = 120000.0, start_date=None, end_date=None) -> pd.DataFrame:
    """
    Agrège les opérations par jour, sépare encaissements et décaissements en DH,
    calcule le flux net journalier et le solde cumulé exact.
    """
    if df.empty:
        return pd.DataFrame(columns=["date", "encaissements", "decaissements", "flux_net", "solde_cumule"])

    df_copy = df.copy()
    df_copy["date"] = pd.to_datetime(df_copy["date"])
    
    # Filtrage par plage de dates
    if start_date:
        df_copy = df_copy[df_copy["date"] >= pd.to_datetime(start_date)]
    if end_date:
        df_copy = df_copy[df_copy["date"] <= pd.to_datetime(end_date)]
        
    if df_copy.empty:
        return pd.DataFrame(columns=["date", "encaissements", "decaissements", "flux_net", "solde_cumule"])

    min_date = df_copy["date"].min()
    max_date = df_copy["date"].max()
    all_dates = pd.date_range(start=min_date, end=max_date, freq="D")
    
    # Pivot des encaissements / décaissements sur montant TTC (flux de trésorerie réel)
    pivot = df_copy.groupby(["date", "type"])["montant"].sum().unstack(fill_value=0.0).reset_index()
    if "Encaissement" not in pivot.columns:
        pivot["Encaissement"] = 0.0
    if "Décaissement" not in pivot.columns:
        pivot["Décaissement"] = 0.0

    full_calendar = pd.DataFrame({"date": all_dates})
    daily = pd.merge(full_calendar, pivot, on="date", how="left").fillna(0.0)
    daily.rename(columns={"Encaissement": "encaissements", "Décaissement": "decaissements"}, inplace=True)

    daily["flux_net"] = daily["encaissements"] - daily["decaissements"]
    daily["solde_cumule"] = initial_balance + daily["flux_net"].cumsum()
    daily["date_str"] = daily["date"].dt.strftime("%Y-%m-%d")

    return daily

def compute_kpis(df: pd.DataFrame, initial_balance: float = 120000.0, forecast_df: pd.DataFrame = None):
    """
    Calcule l'ensemble des KPIs financiers en Dirhams Marocains (DH) :
    - Solde actuel des liquidités
    - Total des encaissements & décaissements
    - Solde prévisionnel à horizon
    - Créances clients (factures clients en attente de règlement)
    - Dettes fournisseurs (factures fournisseurs à régler)
    - Créances échues en retard & Dettes échues
    - Paiements à venir sous 30 jours
    - Position de TVA (collectée, déductible, nette due DGI)
    - Niveau de risque de trésorerie
    """
    today_dt = pd.to_datetime(get_today_morocco())
    today_str = today_dt.strftime("%Y-%m-%d")

    if df.empty:
        return {
            "solde_actuel": initial_balance,
            "total_encaissements": 0.0,
            "total_decaissements": 0.0,
            "solde_net": 0.0,
            "solde_previsionnel": initial_balance,
            "creances_clients": 0.0,
            "dettes_fournisseurs": 0.0,
            "creances_echues": 0.0,
            "dettes_echues": 0.0,
            "paiements_a_venir": 0.0,
            "solde_net_engagements": initial_balance,
            "tva_collectee": 0.0,
            "tva_deductible": 0.0,
            "tva_due": 0.0,
            "variation_valeur": 0.0,
            "variation_pct": 0.0,
            "niveau_risque": "Faible",
            "risque_couleur": "#22C55E"
        }

    daily = compute_daily_cashflow(df, initial_balance=initial_balance)
    past_daily = daily[daily["date"] <= today_dt]
    
    if not past_daily.empty:
        solde_actuel = past_daily["solde_cumule"].iloc[-1]
    else:
        solde_actuel = initial_balance

    total_encaissements = df[df["type"] == "Encaissement"]["montant"].sum()
    total_decaissements = df[df["type"] == "Décaissement"]["montant"].sum()
    solde_net = total_encaissements - total_decaissements

    # Solde prévisionnel
    if forecast_df is not None and not forecast_df.empty:
        solde_previsionnel = forecast_df["solde_prevu"].iloc[-1]
    else:
        solde_previsionnel = daily["solde_cumule"].iloc[-1] if not daily.empty else initial_balance

    variation_valeur = solde_previsionnel - solde_actuel
    if abs(solde_actuel) > 0.01:
        variation_pct = (variation_valeur / abs(solde_actuel)) * 100.0
    else:
        variation_pct = 0.0

    # 1. Créances Clients (Factures clients à encaisser)
    prev_enc = df[(df["type"] == "Encaissement") & (df["statut"] == "Prévu")]
    creances_clients = prev_enc["montant"].sum() if not prev_enc.empty else 0.0

    # Créances échues en retard
    prev_enc_echues = df[(df["type"] == "Encaissement") & (df["statut"] == "Prévu") & (df["date_echeance"] < today_str)]
    creances_echues = prev_enc_echues["montant"].sum() if not prev_enc_echues.empty else 0.0

    # 2. Dettes Fournisseurs (Factures fournisseurs à décaisser)
    prev_dec = df[(df["type"] == "Décaissement") & (df["statut"] == "Prévu")]
    dettes_fournisseurs = prev_dec["montant"].sum() if not prev_dec.empty else 0.0

    # Dettes échues en retard
    prev_dec_echues = df[(df["type"] == "Décaissement") & (df["statut"] == "Prévu") & (df["date_echeance"] < today_str)]
    dettes_echues = prev_dec_echues["montant"].sum() if not prev_dec_echues.empty else 0.0

    # 3. Paiements à venir sous 30 jours
    horizon_30 = (today_dt + timedelta(days=30)).strftime("%Y-%m-%d")
    dec_30 = df[(df["type"] == "Décaissement") & (df["statut"] == "Prévu") & (df["date_echeance"] <= horizon_30)]
    paiements_a_venir = dec_30["montant"].sum() if not dec_30.empty else dettes_fournisseurs

    # Solde net après engagements court terme
    solde_net_engagements = solde_actuel + creances_clients - dettes_fournisseurs

    # 4. Position fiscale de TVA marocaine (CGI)
    if "montant_tva" in df.columns:
        real_df = df[df["statut"] == "Réalisé"]
        tva_collectee = real_df[real_df["type"] == "Encaissement"]["montant_tva"].sum()
        tva_deductible = real_df[real_df["type"] == "Décaissement"]["montant_tva"].sum()
        tva_due = max(0.0, tva_collectee - tva_deductible)
    else:
        tva_collectee, tva_deductible, tva_due = 0.0, 0.0, 0.0

    # Évaluation du risque de trésorerie en DH
    min_future_balance = solde_previsionnel
    if forecast_df is not None and not forecast_df.empty:
        min_future_balance = min(solde_actuel, forecast_df["solde_prevu"].min())
    elif not daily.empty:
        min_future_balance = daily["solde_cumule"].min()

    if min_future_balance < 0:
        niveau_risque = "Critique"
        risque_couleur = "#EF4444"  # Rouge
    elif min_future_balance < 25000:
        niveau_risque = "Élevé"
        risque_couleur = "#F97316"  # Orange vif
    elif min_future_balance < 60000 or (dettes_fournisseurs > (creances_clients + solde_actuel)):
        niveau_risque = "Modéré"
        risque_couleur = "#F59E0B"  # Ambre
    else:
        niveau_risque = "Faible"
        risque_couleur = "#22C55E"  # Vert

    return {
        "solde_actuel": round(solde_actuel, 2),
        "total_encaissements": round(total_encaissements, 2),
        "total_decaissements": round(total_decaissements, 2),
        "solde_net": round(solde_net, 2),
        "solde_previsionnel": round(solde_previsionnel, 2),
        "creances_clients": round(creances_clients, 2),
        "dettes_fournisseurs": round(dettes_fournisseurs, 2),
        "creances_echues": round(creances_echues, 2),
        "dettes_echues": round(dettes_echues, 2),
        "paiements_a_venir": round(paiements_a_venir, 2),
        "solde_net_engagements": round(solde_net_engagements, 2),
        "tva_collectee": round(tva_collectee, 2),
        "tva_deductible": round(tva_deductible, 2),
        "tva_due": round(tva_due, 2),
        "variation_valeur": round(variation_valeur, 2),
        "variation_pct": round(variation_pct, 1),
        "min_future_balance": round(min_future_balance, 2),
        "niveau_risque": niveau_risque,
        "risque_couleur": risque_couleur
    }

def compute_advanced_metrics(df: pd.DataFrame, initial_balance: float = 120000.0):
    """
    Calcule les métriques avancées d'analyse financière adaptées au contexte marocain :
    - Burn Rate journalier (dépenses quotidiennes moyennes en DH)
    - Runway (autonomie en jours)
    - Ratio de couverture
    - Décomposition catégorielle
    """
    if df.empty:
        return {}

    daily = compute_daily_cashflow(df, initial_balance=initial_balance)
    kpis = compute_kpis(df, initial_balance)

    total_days = max(1, (daily["date"].max() - daily["date"].min()).days + 1)
    avg_daily_burn = df[df["type"] == "Décaissement"]["montant"].sum() / total_days

    if avg_daily_burn > 0:
        runway_days = max(0, int(kpis["solde_actuel"] / avg_daily_burn))
    else:
        runway_days = 999

    dec = kpis["total_decaissements"]
    enc = kpis["total_encaissements"]
    coverage_ratio = round((enc / dec), 2) if dec > 0 else 99.0

    # Répartition des dépenses
    dec_df = df[df["type"] == "Décaissement"]
    cat_expenses = dec_df.groupby("categorie")["montant"].sum().reset_index()
    cat_expenses = cat_expenses.sort_values(by="montant", ascending=False)
    cat_expenses["pct"] = round((cat_expenses["montant"] / max(1.0, dec)) * 100, 1)

    # Répartition des encaissements
    enc_df = df[df["type"] == "Encaissement"]
    cat_inflows = enc_df.groupby("categorie")["montant"].sum().reset_index()
    cat_inflows = cat_inflows.sort_values(by="montant", ascending=False)
    cat_inflows["pct"] = round((cat_inflows["montant"] / max(1.0, enc)) * 100, 1)

    return {
        "avg_daily_burn": round(avg_daily_burn, 2),
        "runway_days": runway_days,
        "coverage_ratio": coverage_ratio,
        "cat_expenses": cat_expenses,
        "cat_inflows": cat_inflows,
        "total_days": total_days
    }

def detect_alerts_and_recommendations(df: pd.DataFrame, initial_balance: float = 120000.0, forecast_df: pd.DataFrame = None, security_threshold: float = 25000.0):
    """
    Génère des alertes et recommandations financières fondées sur les pratiques marocaines :
    - Découvert bancaire / facilité de caisse
    - Matelas de sécurité en DH
    - Créances clients en retard de recouvrement
    - Dettes fournisseurs et risques d'agios
    - Échéances de TVA DGI et cotisations CNSS
    """
    alerts = []
    if df.empty:
        return alerts

    kpis = compute_kpis(df, initial_balance, forecast_df)
    adv = compute_advanced_metrics(df, initial_balance)

    # 1. Alerte : Risque de découvert bancaire dans les prévisions
    if forecast_df is not None and not forecast_df.empty:
        negative_forecasts = forecast_df[forecast_df["solde_prevu"] < 0]
        sub_security_forecasts = forecast_df[(forecast_df["solde_prevu"] >= 0) & (forecast_df["solde_prevu"] < security_threshold)]

        if not negative_forecasts.empty:
            first_neg = negative_forecasts.iloc[0]
            val_fmt = format_dh(first_neg['solde_prevu'])
            alerts.append({
                "gravite": "Critique",
                "couleur": "#EF4444",
                "titre": "Risque imminent de découvert bancaire",
                "date": first_neg["date_str"],
                "raison": f"Le solde de trésorerie prévisionnel devient négatif ({val_fmt}) dès le {first_neg['date_str']}.",
                "recommandation": "Négocier en urgence une facilité de caisse avec votre chargé d'affaires bancaire (Attijariwafa, BCP, Bank of Africa) ou mobiliser des créances par cession d'effets / affacturage."
            })
        elif not sub_security_forecasts.empty:
            first_warn = sub_security_forecasts.iloc[0]
            val_fmt = format_dh(first_warn['solde_prevu'])
            seuil_fmt = format_dh(security_threshold)
            alerts.append({
                "gravite": "Élevé",
                "couleur": "#F97316",
                "titre": "Passage sous le matelas de sécurité marocain",
                "date": first_warn["date_str"],
                "raison": f"Le solde prévisionnel atteint {val_fmt} le {first_warn['date_str']}, inférieur au seuil de précaution fixé à {seuil_fmt}.",
                "recommandation": "Accélérer le recouvrement des traites et factures clients échues, et différer les règlements de charges non prioritaires."
            })

    # 2. Alerte : Créances clients en retard de paiement
    if kpis["creances_echues"] > 0:
        cr_fmt = format_dh(kpis["creances_echues"])
        alerts.append({
            "gravite": "Élevé",
            "couleur": "#F97316",
            "titre": "Retard de recouvrement des créances clients",
            "date": "Échéances dépassées",
            "raison": f"Un volume total de {cr_fmt} de factures clients est actuellement échu sans confirmation d'encaissement.",
            "recommandation": "Relancer immédiatement les clients en retard de paiement et exiger le règlement des traites ou virements bancaires sous 48h."
        })

    # 3. Alerte : Dépenses d'exploitation supérieures aux recettes
    if kpis["total_decaissements"] > kpis["total_encaissements"]:
        deficit_fmt = format_dh(kpis["total_decaissements"] - kpis["total_encaissements"])
        alerts.append({
            "gravite": "Modéré",
            "couleur": "#F59E0B",
            "titre": "Déficit d'exploitation sur la période",
            "date": "Période active",
            "raison": f"Les décaissements globaux dépassent les encaissements d'un montant net de {deficit_fmt}.",
            "recommandation": "Analyser la rentabilité des prestations de services, réduire les charges d'achats externes et revoir les conditions de paiement accordées aux clients."
        })

    # 4. Alerte : Dépense inhabituellement élevée (détection statistique)
    dec_df = df[df["type"] == "Décaissement"].copy()
    if len(dec_df) >= 10:
        mean_dec = dec_df["montant"].mean()
        std_dec = dec_df["montant"].std()
        outliers = dec_df[dec_df["montant"] > (mean_dec + 2.2 * std_dec)]
        for _, row in outliers.head(2).iterrows():
            m_fmt = format_dh(row['montant'])
            moy_fmt = format_dh(mean_dec)
            alerts.append({
                "gravite": "Modéré",
                "couleur": "#3B82F6",
                "titre": "Décaissement exceptionnel détecté",
                "date": row["date"],
                "raison": f"Opération '{row['libelle']}' d'un montant de {m_fmt} très supérieur à la moyenne des charges ({moy_fmt}).",
                "recommandation": f"Contrôler la pièce justificative (facture fournisseur ou avis de débit) pour le partenaire '{row.get('partenaire', 'N/A')}'."
            })

    # 5. Alerte : Autonomie de trésorerie (Runway) tendue
    runway = adv.get("runway_days", 999)
    if runway < 30 and kpis["solde_actuel"] > 0:
        alerts.append({
            "gravite": "Élevé",
            "couleur": "#F97316",
            "titre": "Autonomie de trésorerie sous tension",
            "date": "Court terme (< 30 jours)",
            "raison": f"Les liquidités actuelles permettent de couvrir seulement {runway} jours de charges opérationnelles au rythme moyen.",
            "recommandation": "Sécuriser les encaissements contractuels ou solliciter un financement de trésorerie (découvert, escompte ou apport en compte courant)."
        })

    # 6. Alerte positive si situation saine
    if not alerts:
        alerts.append({
            "gravite": "Info",
            "couleur": "#22C55E",
            "titre": "Trésorerie équilibrée et pérenne",
            "date": "Situation actuelle",
            "raison": f"Les encaissements couvrent confortablement les décaissements (ratio de couverture : {adv.get('coverage_ratio', 1.0):.2f}) et aucun découvert n'est anticipé.",
            "recommandation": "Maintenir la rigueur de suivi et placer les excédents temporaires sur des dépôts à terme (DAT) rémunérés en banque."
        })

    return alerts

def generate_executive_summary(kpis: dict, adv: dict, alerts: list) -> str:
    """Génère une synthèse managériale en Dirhams Marocains (DH)."""
    solde_fmt = format_dh(kpis.get("solde_actuel", 0))
    solde_prev_fmt = format_dh(kpis.get("solde_previsionnel", 0))
    var_fmt = format_dh(abs(kpis.get("variation_valeur", 0)))
    ratio = adv.get("coverage_ratio", 1.0)
    runway = adv.get("runway_days", 999)
    cr_fmt = format_dh(kpis.get("creances_clients", 0))
    det_fmt = format_dh(kpis.get("dettes_fournisseurs", 0))
    
    sens_var = "en hausse de" if kpis.get("variation_valeur", 0) >= 0 else "en baisse de"
    
    summary = f"""
**Diagnostic de trésorerie SmartCash AI (Contexte Marocain) :**  
La trésorerie disponible s'élève actuellement à **{solde_fmt}**. Les projections indiquent un solde prévisionnel estimé à **{solde_prev_fmt}**, soit une trajectoire {sens_var} **{var_fmt}** ({kpis.get('variation_pct', 0):+.1f}%).  
Le ratio de couverture des dépenses par les recettes est de **{ratio:.2f}** (cible de sécurité recommandée : > 1.10).  
Le portefeuille des engagements à court terme comprend **{cr_fmt} de créances clients** et **{det_fmt} de dettes fournisseurs**.
    """.strip()
    
    if runway < 45:
        summary += f"\n\n⚠️ **Point de vigilance :** L'autonomie de trésorerie est estimée à **{runway} jours** au rythme moyen des décaissements."
    else:
        summary += f"\n\n✅ **Point fort :** L'entreprise bénéficie d'une autonomie confortable de **{runway} jours** d'exploitation."
        
    crit_count = sum(1 for a in alerts if a["gravite"] in ["Critique", "Élevé"])
    if crit_count > 0:
        summary += f" **{crit_count} alerte(s) prioritaire(s)** requièrent une décision du gestionnaire."
        
    return summary
