"""
SmartCash AI - Gestionnaire de Données Financières (Adaptation Maroc 🇲🇦)
Module data_manager.py
Prend en charge le contexte marocain (MAD / DH), fuseau Africa/Casablanca,
PCGE marocain, gestion de la TVA marocaine (20%, 14%, 10%, 7%, 0%),
suivi des factures (HT, TVA, TTC, Échéances, Créances & Dettes) et persistance locale.
"""

import os
import io
import re
import uuid
import unicodedata
from zoneinfo import ZoneInfo
from datetime import datetime, date, timedelta
import numpy as np
import pandas as pd

# Fuseau horaire marocain
TZ_CASABLANCA = ZoneInfo("Africa/Casablanca")

def get_now_morocco() -> datetime:
    """Retourne l'horodatage courant dans le fuseau horaire de Casablanca."""
    return datetime.now(TZ_CASABLANCA)

def get_today_morocco() -> date:
    """Retourne la date du jour au Maroc."""
    return get_now_morocco().date()

def format_dh(val: float, include_symbol: bool = True) -> str:
    """
    Formate un montant selon les standards financiers marocains :
    Ex: 15 000,00 DH (espace pour séparer les milliers, virgule pour les décimales).
    """
    try:
        val = float(val)
    except (ValueError, TypeError):
        return "0,00 DH" if include_symbol else "0,00"
    
    is_neg = val < 0
    val_abs = abs(val)
    # Formatage standard 15,000.00 -> 15 000,00
    formatted = f"{val_abs:,.2f}".replace(",", " ").replace(".", ",")
    sign = "-" if is_neg else ""
    return f"{sign}{formatted} DH" if include_symbol else f"{sign}{formatted}"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
STORAGE_FILE = os.path.join(DATA_DIR, "transactions.csv")
SAMPLE_FILE = os.path.join(DATA_DIR, "sample_data.csv")
TEMPLATE_CSV = os.path.join(DATA_DIR, "modele_smartcash.csv")
TEMPLATE_XLSX = os.path.join(DATA_DIR, "modele_smartcash.xlsx")

# Catégories conformes au Plan Comptable Général des Entreprises (PCGE) Maroc
CATEGORIES_ENCAISSEMENT = [
    "Ventes de marchandises au Maroc (Cte 7111)",
    "Prestations de services & Produits d'exploitation (Cte 712)",
    "Ventes de biens et services à l'export (Cte 7113/7127)",
    "Financements bancaires, Emprunts & Subventions (Cte 148)",
    "Remboursements reçus & Produits financiers (Cte 738)",
    "Autres encaissements divers (Cte 758)"
]

CATEGORIES_DECAISSEMENT = [
    "Fournisseurs & Achats de marchandises / matières (Cte 611/612)",
    "Rémunérations du personnel & Salaires nets (Cte 6171)",
    "Charges sociales (CNSS, AMO, CIMR) (Cte 6174)",
    "Loyers commerciaux & Charges locatives (Cte 6131)",
    "TVA due à l'État (DGI Maroc) (Cte 4455)",
    "Impôts et taxes (IS, IR, Taxe Professionnelle) (Cte 616)",
    "Transports de marchandises & Déplacements (Cte 6142/6143)",
    "Services extérieurs, Électricité & Eau (Lydec/ONEE) (Cte 6133/6134)",
    "Marketing, Publicité & Relations publiques (Cte 6144)",
    "Frais bancaires, Agios & Intérêts des emprunts (Cte 6147/6311)",
    "Autres charges externes d'exploitation"
]

ALL_CATEGORIES = sorted(list(set(CATEGORIES_ENCAISSEMENT + CATEGORIES_DECAISSEMENT)))

# Taux de TVA applicables selon le Code Général des Impôts (CGI) marocain
TAUX_TVA_MAROC = [20.0, 14.0, 10.0, 7.0, 0.0]

REQUIRED_COLUMNS = [
    "id", "date", "date_echeance", "libelle", "type", "categorie",
    "partenaire", "montant_ht", "taux_tva", "montant_tva", "montant",
    "statut", "statut_paiement", "commentaire"
]

def ensure_data_dir():
    """Crée le dossier data s'il n'existe pas."""
    os.makedirs(DATA_DIR, exist_ok=True)

def compute_tva_amounts(montant_ht: float = None, taux_tva: float = 20.0, montant_ttc: float = None):
    """
    Calcule de façon cohérente HT, TVA et TTC selon la réglementation fiscale marocaine.
    TTC = HT + TVA = HT * (1 + taux/100)
    """
    taux = float(taux_tva) if taux_tva is not None else 20.0
    if montant_ht is not None and not np.isnan(montant_ht):
        ht = round(abs(float(montant_ht)), 2)
        tva = round(ht * (taux / 100.0), 2)
        ttc = round(ht + tva, 2)
        return ht, taux, tva, ttc
    elif montant_ttc is not None and not np.isnan(montant_ttc):
        ttc = round(abs(float(montant_ttc)), 2)
        ht = round(ttc / (1.0 + (taux / 100.0)), 2)
        tva = round(ttc - ht, 2)
        return ht, taux, tva, ttc
    else:
        return 0.0, taux, 0.0, 0.0

def generate_sample_data(num_months: int = 5) -> pd.DataFrame:
    """
    Génère un jeu de données fictif mais très réaliste d'une entreprise marocaine :
    Atlas Distribution SARL (Casablanca), active dans le négoce et les services B2B.
    Montants en Dirhams Marocains (DH / MAD).
    """
    ensure_data_dir()
    np.random.seed(42)
    today = get_today_morocco()
    start_date = today - timedelta(days=num_months * 30)
    end_date = today + timedelta(days=35)
    
    records = []
    
    # 1. Loyer commercial bureaux & entrepôt (Casablanca Sidi Maârouf) - 1er de chaque mois
    # Exonéré ou TVA 20% si bail équipé
    cur = start_date.replace(day=1)
    while cur <= end_date:
        if cur >= start_date:
            ht = 18500.00
            taux = 0.0  # Bail nu d'entreprise sans TVA
            tva = 0.0
            ttc = ht
            stt = "Réalisé" if cur <= today else "Prévu"
            stt_p = "Payé" if cur <= today else ("En retard" if cur < today else "En attente")
            records.append({
                "id": str(uuid.uuid4())[:8],
                "date": cur.strftime("%Y-%m-%d"),
                "date_echeance": cur.strftime("%Y-%m-%d"),
                "libelle": f"Loyer bureaux & dépôt Casablanca - {cur.strftime('%m/%Y')}",
                "type": "Décaissement",
                "categorie": "Loyers commerciaux & Charges locatives (Cte 6131)",
                "partenaire": "Société Foncière Anfa",
                "montant_ht": ht,
                "taux_tva": taux,
                "montant_tva": tva,
                "montant": ttc,
                "statut": stt,
                "statut_paiement": stt_p,
                "commentaire": "Bail commercial siège Casablanca"
            })
        year = cur.year + (1 if cur.month == 12 else 0)
        month = 1 if cur.month == 12 else cur.month + 1
        cur = cur.replace(year=year, month=month, day=1)

    # 2. Salaires du personnel (28 de chaque mois) & CNSS / AMO (10 du mois suivant)
    cur = start_date.replace(day=28)
    while cur <= end_date:
        if cur >= start_date:
            net_salaires = round(np.random.uniform(55000, 64000), 2)
            stt = "Réalisé" if cur <= today else "Prévu"
            stt_p = "Payé" if cur <= today else ("En retard" if cur < today else "En attente")
            records.append({
                "id": str(uuid.uuid4())[:8],
                "date": cur.strftime("%Y-%m-%d"),
                "date_echeance": cur.strftime("%Y-%m-%d"),
                "libelle": f"Virement Salaires nets équipe - {cur.strftime('%m/%Y')}",
                "type": "Décaissement",
                "categorie": "Rémunérations du personnel & Salaires nets (Cte 6171)",
                "partenaire": "Personnel entreprise (8 salariés)",
                "montant_ht": net_salaires,
                "taux_tva": 0.0,
                "montant_tva": 0.0,
                "montant": net_salaires,
                "statut": stt,
                "statut_paiement": stt_p,
                "commentaire": "Virement bancaire groupé salaires Attijariwafa"
            })
            
            # Cotisations CNSS & AMO (10 du mois d'après)
            cnss_date = (cur + timedelta(days=12)).replace(day=10)
            if cnss_date <= end_date:
                cnss_montant = round(net_salaires * 0.22, 2)
                stt_cnss = "Réalisé" if cnss_date <= today else "Prévu"
                stt_p_cnss = "Payé" if cnss_date <= today else ("En retard" if cnss_date < today else "En attente")
                records.append({
                    "id": str(uuid.uuid4())[:8],
                    "date": cnss_date.strftime("%Y-%m-%d"),
                    "date_echeance": cnss_date.strftime("%Y-%m-%d"),
                    "libelle": f"Bordereau CNSS & AMO - Échéance {cnss_date.strftime('%m/%Y')}",
                    "type": "Décaissement",
                    "categorie": "Charges sociales (CNSS, AMO, CIMR) (Cte 6174)",
                    "partenaire": "CNSS Maroc",
                    "montant_ht": cnss_montant,
                    "taux_tva": 0.0,
                    "montant_tva": 0.0,
                    "montant": cnss_montant,
                    "statut": stt_cnss,
                    "statut_paiement": stt_p_cnss,
                    "commentaire": "Télé-déclaration Damancom"
                })
        year = cur.year + (1 if cur.month == 12 else 0)
        month = 1 if cur.month == 12 else cur.month + 1
        cur = cur.replace(year=year, month=month, day=28)

    # 3. Déclaration mensuelle TVA à la DGI Maroc (20 de chaque mois)
    cur = start_date.replace(day=20)
    while cur <= end_date:
        if cur >= start_date:
            tva_due = round(np.random.uniform(14000, 26000), 2)
            stt = "Réalisé" if cur <= today else "Prévu"
            stt_p = "Payé" if cur <= today else ("En retard" if cur < today else "En attente")
            records.append({
                "id": str(uuid.uuid4())[:8],
                "date": cur.strftime("%Y-%m-%d"),
                "date_echeance": cur.strftime("%Y-%m-%d"),
                "libelle": f"Télérèglement TVA mensuelle DGI - {cur.strftime('%m/%Y')}",
                "type": "Décaissement",
                "categorie": "TVA due à l'État (DGI Maroc) (Cte 4455)",
                "partenaire": "DGI (Direction Générale des Impôts)",
                "montant_ht": tva_due,
                "taux_tva": 0.0,
                "montant_tva": 0.0,
                "montant": tva_due,
                "statut": stt,
                "statut_paiement": stt_p,
                "commentaire": "Portail SIMPL-TVA"
            })
        year = cur.year + (1 if cur.month == 12 else 0)
        month = 1 if cur.month == 12 else cur.month + 1
        cur = cur.replace(year=year, month=month, day=20)

    # 4. Factures clients / Encaissements (Entreprises marocaines clientes)
    clients_maroc = [
        "Marjane Holding", "Groupe OCP Casablanca", "LabelVie SA",
        "Dislog Group", "Pharma 5", "Cosumar SA", "Sothema Maroc",
        "Inwi Entreprises", "Société Générale Marocaine"
    ]
    curr_day = start_date
    while curr_day <= end_date:
        if curr_day.weekday() not in [5, 6]:
            if np.random.rand() < 0.40:
                client = np.random.choice(clients_maroc)
                ht = round(np.random.choice([
                    np.random.uniform(12000, 35000),
                    np.random.uniform(45000, 85000),
                    np.random.uniform(90000, 160000)
                ], p=[0.50, 0.35, 0.15]), 2)
                taux = 20.0
                tva = round(ht * (taux / 100.0), 2)
                ttc = round(ht + tva, 2)
                
                # Échéance contractuelle à 30 ou 60 jours
                delai = int(np.random.choice([15, 30, 60]))
                echeance = curr_day + timedelta(days=delai)
                stt = "Réalisé" if curr_day <= today else "Prévu"
                
                if stt == "Réalisé":
                    stt_p = "Payé"
                else:
                    stt_p = "En retard" if echeance < today else "En attente"

                records.append({
                    "id": str(uuid.uuid4())[:8],
                    "date": curr_day.strftime("%Y-%m-%d"),
                    "date_echeance": echeance.strftime("%Y-%m-%d"),
                    "libelle": f"Facture client {client} (Réf #FC-{np.random.randint(1000, 9999)})",
                    "type": "Encaissement",
                    "categorie": np.random.choice([
                        "Ventes de marchandises au Maroc (Cte 7111)",
                        "Prestations de services & Produits d'exploitation (Cte 712)"
                    ], p=[0.65, 0.35]),
                    "partenaire": client,
                    "montant_ht": ht,
                    "taux_tva": taux,
                    "montant_tva": tva,
                    "montant": ttc,
                    "statut": stt,
                    "statut_paiement": stt_p,
                    "commentaire": f"Règlement par virement / traite à {delai}j"
                })
        curr_day += timedelta(days=1)

    # 5. Dépenses fournisseurs et achats courants au Maroc
    fournisseurs_maroc = [
        ("Fournisseur Matériel IT Casablanca", 20.0, "Fournisseurs & Achats de marchandises / matières (Cte 611/612)"),
        ("SNTL Transport & Logistique", 14.0, "Transports de marchandises & Déplacements (Cte 6142/6143)"),
        ("Papeterie & Fournitures Maroc", 20.0, "Fournisseurs & Achats de marchandises / matières (Cte 611/612)"),
        ("Agence Web Marketing Rabat", 20.0, "Marketing, Publicité & Relations publiques (Cte 6144)"),
        ("Lydec Eau & Électricité", 14.0, "Services extérieurs, Électricité & Eau (Lydec/ONEE) (Cte 6133/6134)")
    ]
    curr_day = start_date
    while curr_day <= end_date:
        if curr_day.weekday() not in [5, 6]:
            if np.random.rand() < 0.35:
                supp, t_tva, cat_nom = fournisseurs_maroc[np.random.choice(len(fournisseurs_maroc))]
                ht = round(np.random.uniform(1800, 22000), 2)
                tva = round(ht * (t_tva / 100.0), 2)
                ttc = round(ht + tva, 2)
                
                delai = int(np.random.choice([15, 30, 45]))
                echeance = curr_day + timedelta(days=delai)
                stt = "Réalisé" if curr_day <= today else "Prévu"
                stt_p = "Payé" if stt == "Réalisé" else ("En retard" if echeance < today else "En attente")

                records.append({
                    "id": str(uuid.uuid4())[:8],
                    "date": curr_day.strftime("%Y-%m-%d"),
                    "date_echeance": echeance.strftime("%Y-%m-%d"),
                    "libelle": f"Facture {supp} (Réf #FF-{np.random.randint(1000, 9999)})",
                    "type": "Décaissement",
                    "categorie": cat_nom,
                    "partenaire": supp,
                    "montant_ht": ht,
                    "taux_tva": t_tva,
                    "montant_tva": tva,
                    "montant": ttc,
                    "statut": stt,
                    "statut_paiement": stt_p,
                    "commentaire": f"Échéance paiement fournisseur à {delai}j"
                })
        curr_day += timedelta(days=1)

    # 6. Frais bancaires & commissions au Maroc (le 5 de chaque mois)
    curr_day = start_date
    while curr_day <= end_date:
        if curr_day.day == 5:
            ht = round(np.random.uniform(650, 1400), 2)
            taux = 10.0  # TVA bancaire au Maroc = 10%
            tva = round(ht * 0.10, 2)
            ttc = round(ht + tva, 2)
            stt = "Réalisé" if curr_day <= today else "Prévu"
            records.append({
                "id": str(uuid.uuid4())[:8],
                "date": curr_day.strftime("%Y-%m-%d"),
                "date_echeance": curr_day.strftime("%Y-%m-%d"),
                "libelle": "Frais de tenue de compte & commissions bancaires",
                "type": "Décaissement",
                "categorie": "Frais bancaires, Agios & Intérêts des emprunts (Cte 6147/6311)",
                "partenaire": "Attijariwafa bank / BCP",
                "montant_ht": ht,
                "taux_tva": taux,
                "montant_tva": tva,
                "montant": ttc,
                "statut": stt,
                "statut_paiement": "Payé" if stt == "Réalisé" else "En attente",
                "commentaire": "Prélèvement automatique banque (TVA 10%)"
            })
        curr_day += timedelta(days=1)

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df["date_echeance"] = pd.to_datetime(df["date_echeance"]).dt.strftime("%Y-%m-%d")
    df = df.sort_values(by=["date", "type"], ascending=[True, False]).reset_index(drop=True)
    
    # Sauvegarde des démos
    df.to_csv(SAMPLE_FILE, index=False, encoding="utf-8")
    return df

def generate_templates():
    """Génère les modèles CSV et Excel téléchargeables adaptés au contexte marocain."""
    ensure_data_dir()
    today = get_today_morocco()
    sample_rows = [
        {
            "Date": today.strftime("%Y-%m-%d"),
            "Date Échéance": (today + timedelta(days=30)).strftime("%Y-%m-%d"),
            "Libellé": "Vente de marchandises au Maroc #FC-2026-081",
            "Type": "Encaissement",
            "Catégorie": "Ventes de marchandises au Maroc (Cte 7111)",
            "Partenaire": "Groupe OCP Solutions",
            "Montant HT": 45000.00,
            "Taux TVA (%)": 20.0,
            "Montant TVA": 9000.00,
            "Montant TTC (DH)": 54000.00,
            "Statut": "Réalisé",
            "Statut Paiement": "Payé",
            "Commentaire": "Règlement reçu par virement bancaire"
        },
        {
            "Date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
            "Date Échéance": (today + timedelta(days=15)).strftime("%Y-%m-%d"),
            "Libellé": "Paiement fournisseur Matériel IT Casablanca #FF-592",
            "Type": "Décaissement",
            "Catégorie": "Fournisseurs & Achats de marchandises / matières (Cte 611/612)",
            "Partenaire": "Fournisseur Matériel IT",
            "Montant HT": 28000.00,
            "Taux TVA (%)": 20.0,
            "Montant TVA": 5600.00,
            "Montant TTC (DH)": 33600.00,
            "Statut": "Réalisé",
            "Statut Paiement": "Payé",
            "Commentaire": "Règlement facture fournisseur par chèque"
        },
        {
            "Date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            "Date Échéance": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            "Libellé": "Loyer commercial siège Casablanca",
            "Type": "Décaissement",
            "Catégorie": "Loyers commerciaux & Charges locatives (Cte 6131)",
            "Partenaire": "Société Foncière Anfa",
            "Montant HT": 18500.00,
            "Taux TVA (%)": 0.0,
            "Montant TVA": 0.00,
            "Montant TTC (DH)": 18500.00,
            "Statut": "Prévu",
            "Statut Paiement": "En attente",
            "Commentaire": "Chèque de loyer mensuel à émettre"
        },
        {
            "Date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
            "Date Échéance": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
            "Libellé": "Salaires nets du personnel Casablanca",
            "Type": "Décaissement",
            "Catégorie": "Rémunérations du personnel & Salaires nets (Cte 6171)",
            "Partenaire": "Personnel Entreprise (8 salariés)",
            "Montant HT": 55000.00,
            "Taux TVA (%)": 0.0,
            "Montant TVA": 0.00,
            "Montant TTC (DH)": 55000.00,
            "Statut": "Prévu",
            "Statut Paiement": "En attente",
            "Commentaire": "Virement groupé de paie Attijariwafa"
        },
        {
            "Date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
            "Date Échéance": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
            "Libellé": "Vente comptant magasin Casablanca #TK-104",
            "Type": "Encaissement",
            "Catégorie": "Ventes de marchandises au Maroc (Cte 7111)",
            "Partenaire": "Clients Comptant Magasin",
            "Montant HT": 12500.00,
            "Taux TVA (%)": 20.0,
            "Montant TVA": 2500.00,
            "Montant TTC (DH)": 15000.00,
            "Statut": "Réalisé",
            "Statut Paiement": "Payé",
            "Commentaire": "Encaissement caisse espèces / TPE"
        }
    ]
    df_template = pd.DataFrame(sample_rows)
    df_template.to_csv(TEMPLATE_CSV, index=False, encoding="utf-8-sig")
    
    try:
        with pd.ExcelWriter(TEMPLATE_XLSX, engine="openpyxl") as writer:
            df_template.to_excel(writer, sheet_name="Operations_Maroc", index=False)
    except Exception as e:
        print(f"Erreur création template Excel : {e}")

def load_transactions(initial_balance: float = 120000.0) -> pd.DataFrame:
    """
    Charge les transactions existantes avec rétrocompatibilité complète.
    Si des colonnes marocaines (HT, TVA, Échéance, Partenaire) sont absentes,
    elles sont déduites automatiquement et de manière transparente.
    """
    ensure_data_dir()
    if not os.path.exists(SAMPLE_FILE):
        generate_sample_data()
    if not os.path.exists(TEMPLATE_CSV) or not os.path.exists(TEMPLATE_XLSX):
        generate_templates()
        
    if not os.path.exists(STORAGE_FILE):
        sample_df = pd.read_csv(SAMPLE_FILE)
        sample_df.to_csv(STORAGE_FILE, index=False, encoding="utf-8")
        return sample_df

    try:
        df = pd.read_csv(STORAGE_FILE)
        today = get_today_morocco()
        
        # Ajout et complétion des colonnes avec rétrocompatibilité
        if "id" not in df.columns:
            df["id"] = [str(uuid.uuid4())[:8] for _ in range(len(df))]
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        else:
            df["date"] = today.strftime("%Y-%m-%d")

        if "date_echeance" not in df.columns:
            df["date_echeance"] = df["date"]
        else:
            df["date_echeance"] = pd.to_datetime(df["date_echeance"], errors="coerce").fillna(pd.to_datetime(df["date"])).dt.strftime("%Y-%m-%d")

        if "montant" in df.columns:
            df["montant"] = pd.to_numeric(df["montant"], errors="coerce").fillna(0.0).round(2)
        else:
            df["montant"] = 0.0

        if "taux_tva" not in df.columns:
            # Taux normal par défaut
            df["taux_tva"] = 20.0
        else:
            df["taux_tva"] = pd.to_numeric(df["taux_tva"], errors="coerce").fillna(20.0)

        if "montant_ht" not in df.columns:
            df["montant_ht"] = (df["montant"] / (1.0 + (df["taux_tva"] / 100.0))).round(2)
        else:
            df["montant_ht"] = pd.to_numeric(df["montant_ht"], errors="coerce").fillna(
                (df["montant"] / (1.0 + (df["taux_tva"] / 100.0))).round(2)
            )

        if "montant_tva" not in df.columns:
            df["montant_tva"] = (df["montant"] - df["montant_ht"]).round(2)
        else:
            df["montant_tva"] = pd.to_numeric(df["montant_tva"], errors="coerce").fillna(
                (df["montant"] - df["montant_ht"]).round(2)
            )

        if "partenaire" not in df.columns:
            df["partenaire"] = "Divers"
        else:
            df["partenaire"] = df["partenaire"].fillna("Divers").astype(str)

        if "statut" not in df.columns:
            df["statut"] = "Réalisé"

        if "statut_paiement" not in df.columns:
            # Déduire automatiquement
            def deduce_stt_p(row):
                if row["statut"] == "Réalisé":
                    return "Payé"
                ech = str(row["date_echeance"])
                if ech < today.strftime("%Y-%m-%d"):
                    return "En retard"
                return "En attente"
            df["statut_paiement"] = df.apply(deduce_stt_p, axis=1)

        if "commentaire" not in df.columns:
            df["commentaire"] = ""
        else:
            df["commentaire"] = df["commentaire"].fillna("").astype(str)

        return df[REQUIRED_COLUMNS]
    except Exception as e:
        print(f"Erreur chargement transactions : {e}")
        return pd.read_csv(SAMPLE_FILE)

def save_transactions(df: pd.DataFrame) -> bool:
    """Sauvegarde le DataFrame dans le fichier local CSV."""
    ensure_data_dir()
    try:
        df_clean = df.copy()
        if "id" not in df_clean.columns:
            df_clean["id"] = [str(uuid.uuid4())[:8] for _ in range(len(df_clean))]
        for col in REQUIRED_COLUMNS:
            if col not in df_clean.columns:
                df_clean[col] = ""
        df_clean["date"] = pd.to_datetime(df_clean["date"]).dt.strftime("%Y-%m-%d")
        df_clean["date_echeance"] = pd.to_datetime(df_clean["date_echeance"]).dt.strftime("%Y-%m-%d")
        df_clean["montant"] = pd.to_numeric(df_clean["montant"], errors="coerce").fillna(0.0).round(2)
        df_clean.to_csv(STORAGE_FILE, index=False, encoding="utf-8")
        return True
    except Exception as e:
        print(f"Erreur sauvegarde : {e}")
        return False

def add_transaction(
    date_op: str,
    libelle: str,
    type_op: str,
    categorie: str,
    montant: float = None,
    statut: str = "Réalisé",
    commentaire: str = "",
    date_echeance: str = None,
    partenaire: str = "Divers",
    montant_ht: float = None,
    taux_tva: float = 20.0
) -> pd.DataFrame:
    """Ajoute une opération financière marocaine avec calcul HT, TVA et TTC."""
    df = load_transactions()
    today_str = get_today_morocco().strftime("%Y-%m-%d")
    
    # Cohérence HT / TVA / TTC
    ht, taux, tva, ttc = compute_tva_amounts(montant_ht=montant_ht, taux_tva=taux_tva, montant_ttc=montant)
    
    d_op = pd.to_datetime(date_op).strftime("%Y-%m-%d")
    d_ech = pd.to_datetime(date_echeance).strftime("%Y-%m-%d") if date_echeance else d_op

    statut_clean = "Prévu" if ("prévu" in statut.lower() or "prevu" in statut.lower()) else "Réalisé"
    if statut_clean == "Réalisé":
        statut_p = "Payé"
    else:
        statut_p = "En retard" if d_ech < today_str else "En attente"

    new_op = pd.DataFrame([{
        "id": str(uuid.uuid4())[:8],
        "date": d_op,
        "date_echeance": d_ech,
        "libelle": libelle.strip(),
        "type": "Encaissement" if "encaissement" in type_op.lower() else "Décaissement",
        "categorie": categorie.strip(),
        "partenaire": partenaire.strip() if partenaire else "Divers",
        "montant_ht": ht,
        "taux_tva": taux,
        "montant_tva": tva,
        "montant": ttc,
        "statut": statut_clean,
        "statut_paiement": statut_p,
        "commentaire": commentaire.strip() if commentaire else ""
    }])
    df = pd.concat([df, new_op], ignore_index=True)
    df = df.sort_values(by=["date", "type"], ascending=[True, False]).reset_index(drop=True)
    save_transactions(df)
    return df

def update_transaction(
    op_id: str,
    date_op: str,
    libelle: str,
    type_op: str,
    categorie: str,
    montant: float = None,
    statut: str = "Réalisé",
    commentaire: str = "",
    date_echeance: str = None,
    partenaire: str = "Divers",
    montant_ht: float = None,
    taux_tva: float = 20.0
) -> pd.DataFrame:
    """Modifie une opération existante par son ID."""
    df = load_transactions()
    idx = df[df["id"] == op_id].index
    if len(idx) > 0:
        ht, taux, tva, ttc = compute_tva_amounts(montant_ht=montant_ht, taux_tva=taux_tva, montant_ttc=montant)
        d_op = pd.to_datetime(date_op).strftime("%Y-%m-%d")
        d_ech = pd.to_datetime(date_echeance).strftime("%Y-%m-%d") if date_echeance else d_op
        today_str = get_today_morocco().strftime("%Y-%m-%d")

        statut_clean = "Prévu" if ("prévu" in statut.lower() or "prevu" in statut.lower()) else "Réalisé"
        if statut_clean == "Réalisé":
            statut_p = "Payé"
        else:
            statut_p = "En retard" if d_ech < today_str else "En attente"

        df.loc[idx, "date"] = d_op
        df.loc[idx, "date_echeance"] = d_ech
        df.loc[idx, "libelle"] = libelle.strip()
        df.loc[idx, "type"] = "Encaissement" if "encaissement" in type_op.lower() else "Décaissement"
        df.loc[idx, "categorie"] = categorie.strip()
        df.loc[idx, "partenaire"] = partenaire.strip() if partenaire else "Divers"
        df.loc[idx, "montant_ht"] = ht
        df.loc[idx, "taux_tva"] = taux
        df.loc[idx, "montant_tva"] = tva
        df.loc[idx, "montant"] = ttc
        df.loc[idx, "statut"] = statut_clean
        df.loc[idx, "statut_paiement"] = statut_p
        df.loc[idx, "commentaire"] = commentaire.strip() if commentaire else ""
        
        df = df.sort_values(by=["date", "type"], ascending=[True, False]).reset_index(drop=True)
        save_transactions(df)
    return df

def delete_transaction(op_id: str) -> pd.DataFrame:
    """Supprime une opération par son ID."""
    df = load_transactions()
    df = df[df["id"] != op_id].reset_index(drop=True)
    save_transactions(df)
    return df

def reset_to_sample_data() -> pd.DataFrame:
    """Réinitialise les transactions avec le jeu de données démo marocain."""
    ensure_data_dir()
    df_sample = generate_sample_data()
    df_sample.to_csv(STORAGE_FILE, index=False, encoding="utf-8")
    return df_sample

def normalize_text(text: str) -> str:
    """Supprime les accents, caractères spéciaux et met en minuscules."""
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    nfkd = unicodedata.normalize('NFKD', text)
    ascii_text = "".join([c for c in nfkd if not unicodedata.combining(c)])
    clean = re.sub(r'[^a-zA-Z0-9]+', '_', ascii_text.lower().strip()).strip('_')
    return clean

def map_imported_columns(columns) -> dict:
    """
    Associe de manière intelligente et déterministe les colonnes du fichier
    importé aux champs standard de SmartCash AI, indépendamment de leur ordre ou casse.
    """
    mapping = {}
    used_targets = set()
    cleaned_cols = {col: normalize_text(col) for col in columns}

    # 1. Date d'échéance (prioritaire sur date simple pour éviter les faux positifs)
    for col, slug in cleaned_cols.items():
        if any(k in slug for k in ["echeance", "date_echeance", "date_limite", "due_date"]) and "date_echeance" not in used_targets:
            mapping[col] = "date_echeance"
            used_targets.add("date_echeance")
            break

    # 2. Date d'opération
    for col, slug in cleaned_cols.items():
        if col not in mapping and ("date" in slug or "jour" in slug or slug in ["dt", "periode", "date_op", "date_valeur"]) and "date" not in used_targets:
            mapping[col] = "date"
            used_targets.add("date")
            break

    # 3. Type d'opération (Sens / Nature / Flux / Mouvement)
    for col, slug in cleaned_cols.items():
        if col not in mapping:
            if slug in ["type", "sens", "nature", "flux", "mouvement", "type_op", "sens_op", "type_operation"] or (
                ("type" in slug or "sens" in slug or "flux" in slug) and not any(k in slug for k in ["tiers", "partenaire", "client", "fournisseur", "paiement", "compte"])
            ):
                if "type" not in used_targets:
                    mapping[col] = "type"
                    used_targets.add("type")
                    break

    # 4. Colonnes Débit / Crédit séparées (si relevé bancaire à 2 colonnes de flux)
    for col, slug in cleaned_cols.items():
        if col not in mapping:
            if slug in ["credit", "encaissement", "recette", "entree", "entrees", "credits"] or slug.startswith("credit_"):
                if "col_credit" not in used_targets:
                    mapping[col] = "col_credit"
                    used_targets.add("col_credit")
                    break

    for col, slug in cleaned_cols.items():
        if col not in mapping:
            if slug in ["debit", "decaissement", "depense", "sortie", "sorties", "debits"] or slug.startswith("debit_"):
                if "col_debit" not in used_targets:
                    mapping[col] = "col_debit"
                    used_targets.add("col_debit")
                    break

    # 5. Montant HT
    for col, slug in cleaned_cols.items():
        if col not in mapping:
            if ("ht" in slug or "hors_taxe" in slug) and not any(k in slug for k in ["taux", "pct", "pourcent"]):
                if "montant_ht" not in used_targets:
                    mapping[col] = "montant_ht"
                    used_targets.add("montant_ht")
                    break

    # 6. Taux TVA (%)
    for col, slug in cleaned_cols.items():
        if col not in mapping:
            if ("tva" in slug and any(k in slug for k in ["taux", "pct", "pourcent", "%"])) or slug in ["taux_tva", "tva_taux"]:
                if "taux_tva" not in used_targets:
                    mapping[col] = "taux_tva"
                    used_targets.add("taux_tva")
                    break

    # 7. Montant TVA (en valeur DH)
    for col, slug in cleaned_cols.items():
        if col not in mapping:
            if "tva" in slug and any(k in slug for k in ["montant", "valeur", "dh", "mad"]):
                if "montant_tva" not in used_targets:
                    mapping[col] = "montant_tva"
                    used_targets.add("montant_tva")
                    break

    # 8. Montant TTC / Total (ou montant unique)
    for col, slug in cleaned_cols.items():
        if col not in mapping:
            if any(k in slug for k in ["ttc", "montant_ttc", "total_ttc"]):
                if "montant" not in used_targets:
                    mapping[col] = "montant"
                    used_targets.add("montant")
                    break

    # 9. Montant générique si TTC non trouvé
    if "montant" not in used_targets and "col_credit" not in used_targets:
        for col, slug in cleaned_cols.items():
            if col not in mapping:
                if slug in ["montant", "montant_dh", "montant_mad", "total", "valeur", "somme", "prix"]:
                    mapping[col] = "montant"
                    used_targets.add("montant")
                    break

    # 10. Libellé / Désignation / Description
    for col, slug in cleaned_cols.items():
        if col not in mapping:
            if any(k in slug for k in ["libelle", "designation", "description", "motif", "operation", "intitule", "details"]):
                if "libelle" not in used_targets:
                    mapping[col] = "libelle"
                    used_targets.add("libelle")
                    break

    # 11. Catégorie PCGE
    for col, slug in cleaned_cols.items():
        if col not in mapping:
            if any(k in slug for k in ["categorie", "rubrique", "poste", "classification"]):
                if "categorie" not in used_targets:
                    mapping[col] = "categorie"
                    used_targets.add("categorie")
                    break

    # 12. Partenaire / Tiers / Client / Fournisseur
    for col, slug in cleaned_cols.items():
        if col not in mapping:
            if any(k in slug for k in ["partenaire", "client", "fournisseur", "tiers", "beneficiaire"]):
                if "partenaire" not in used_targets:
                    mapping[col] = "partenaire"
                    used_targets.add("partenaire")
                    break

    # 13. Statut de paiement (Payé / En attente / En retard)
    for col, slug in cleaned_cols.items():
        if col not in mapping:
            if "paiement" in slug and ("statut" in slug or "etat" in slug):
                if "statut_paiement" not in used_targets:
                    mapping[col] = "statut_paiement"
                    used_targets.add("statut_paiement")
                    break

    # 14. Statut d'opération (Réalisé / Prévu)
    for col, slug in cleaned_cols.items():
        if col not in mapping:
            if slug in ["statut", "etat"]:
                if "statut" not in used_targets:
                    mapping[col] = "statut"
                    used_targets.add("statut")
                    break

    # 15. Commentaire
    for col, slug in cleaned_cols.items():
        if col not in mapping:
            if any(k in slug for k in ["commentaire", "commentaires", "note", "notes", "remarque"]):
                if "commentaire" not in used_targets:
                    mapping[col] = "commentaire"
                    used_targets.add("commentaire")
                    break

    return mapping

def resolve_operation_type(raw_type_val, libelle: str = "", montant: float = 0.0, categorie: str = "") -> str:
    """
    Détermine avec certitude le type d'opération : 'Encaissement' ou 'Décaissement'.
    Ne transforme JAMAIS un décaissement en encaissement.
    Gère les accents, encodages et abréviations.
    """
    if pd.notna(raw_type_val):
        t_clean = re.sub(r'[^a-zA-Z]', '', unicodedata.normalize('NFKD', str(raw_type_val))).lower()
        
        # 1. Vérification Encaissement explicite
        if "encais" in t_clean or "credit" in t_clean or "recette" in t_clean or "revenu" in t_clean or "entree" in t_clean or "inflow" in t_clean or "gain" in t_clean or "versement" in t_clean:
            return "Encaissement"
        if t_clean in ["c", "cr", "e", "in"]:
            return "Encaissement"

        # 2. Vérification Décaissement explicite (gère décaissement, decaissement, dcaissement, décais, etc.)
        if "cais" in t_clean or "debit" in t_clean or "depense" in t_clean or "charge" in t_clean or "sortie" in t_clean or "outflow" in t_clean or "retrait" in t_clean or "frais" in t_clean:
            return "Décaissement"
        if t_clean in ["d", "dr", "out", "fournisseur", "achat", "loyer", "salaire", "salaires", "paie"]:
            return "Décaissement"
        if t_clean in ["client", "vente", "ventes", "comptant"]:
            return "Encaissement"

    # 3. Si la colonne Type est absente ou vide, inspecter le signe numérique du montant
    if isinstance(montant, (int, float)) and montant < 0:
        return "Décaissement"
    if str(montant).strip().startswith("-"):
        return "Décaissement"

    # 4. Indices contextuels explicites dans le libellé et la catégorie
    ctx = re.sub(r'[^a-zA-Z]', '', unicodedata.normalize('NFKD', f"{libelle} {categorie}")).lower()

    dec_keywords = [
        "fournisseur", "loyer", "salaire", "salaires", "paie", "achat", "achats",
        "cnss", "amo", "cimr", "dgi", "simpl", "lydec", "onee", "telecom", "carburant",
        "assurance", "transport", "frais", "charge"
    ]
    enc_keywords = [
        "client", "vente", "ventes", "recette", "comptant", "subvention",
        "remboursement", "facturation", "export"
    ]

    has_dec = any(k in ctx for k in dec_keywords)
    has_enc = any(k in ctx for k in enc_keywords)

    if has_dec and not has_enc:
        return "Décaissement"
    if has_enc and not has_dec:
        return "Encaissement"

    # Par défaut (recette)
    return "Encaissement"

def compute_operation_signature(date_str: str, type_val: str, montant_val: float, libelle_val: str, partenaire_val: str = "") -> str:
    """Calcule une empreinte unique pour identifier rigoureusement les doublons réels."""
    m = f"{abs(float(montant_val)):.2f}"
    l_norm = normalize_text(str(libelle_val))
    p_norm = normalize_text(str(partenaire_val))
    return f"{date_str}|{type_val}|{m}|{l_norm}|{p_norm}"

def parse_and_validate_import(file_buffer, filename: str, existing_df: pd.DataFrame = None):
    """
    Lit un fichier importé (.csv ou .xlsx), associe les colonnes indépendamment de leur ordre,
    respecte strictement les types Encaissement/Décaissement, valide la TVA marocaine
    et filtre intelligemment les doublons sans bloquer les opérations légitimes.
    """
    errors = []
    try:
        if filename.endswith(".csv"):
            try:
                raw_df = pd.read_csv(file_buffer, encoding="utf-8")
            except Exception:
                file_buffer.seek(0)
                try:
                    raw_df = pd.read_csv(file_buffer, encoding="latin-1", sep=";")
                except Exception:
                    file_buffer.seek(0)
                    raw_df = pd.read_csv(file_buffer, sep=None, engine="python")
        elif filename.endswith((".xlsx", ".xls")):
            raw_df = pd.read_excel(file_buffer)
        else:
            empty_stats = {"total_lignes": 0, "nb_encaissements": 0, "total_encaissements": 0.0, "nb_decaissements": 0, "total_decaissements": 0.0, "nb_doublons": 0, "nb_rejetes": 1}
            return None, ["Format de fichier non pris en charge. Veuillez utiliser un fichier .csv ou .xlsx."], 0, empty_stats
    except Exception as e:
        empty_stats = {"total_lignes": 0, "nb_encaissements": 0, "total_encaissements": 0.0, "nb_decaissements": 0, "total_decaissements": 0.0, "nb_doublons": 0, "nb_rejetes": 1}
        return None, [f"Erreur lors de la lecture du fichier : {str(e)}"], 0, empty_stats

    if raw_df.empty:
        empty_stats = {"total_lignes": 0, "nb_encaissements": 0, "total_encaissements": 0.0, "nb_decaissements": 0, "total_decaissements": 0.0, "nb_doublons": 0, "nb_rejetes": 1}
        return None, ["Le fichier importé est vide."], 0, empty_stats

    # 1. Association robuste des colonnes, peu importe leur ordre ou casse
    col_mapping = map_imported_columns(raw_df.columns)
    raw_df = raw_df.rename(columns=col_mapping)

    # Vérification des colonnes minimales indispensables
    if "date" not in raw_df.columns:
        empty_stats = {"total_lignes": len(raw_df), "nb_encaissements": 0, "total_encaissements": 0.0, "nb_decaissements": 0, "total_decaissements": 0.0, "nb_doublons": 0, "nb_rejetes": 1}
        return None, ["La colonne 'Date' (ou 'Date d'opération') est obligatoire."], 0, empty_stats

    has_amount = ("montant" in raw_df.columns or "montant_ht" in raw_df.columns or ("col_credit" in raw_df.columns and "col_debit" in raw_df.columns))
    if not has_amount:
        empty_stats = {"total_lignes": len(raw_df), "nb_encaissements": 0, "total_encaissements": 0.0, "nb_decaissements": 0, "total_decaissements": 0.0, "nb_doublons": 0, "nb_rejetes": 1}
        return None, ["Au moins une colonne de montant ('Montant TTC', 'Montant HT', ou colonnes 'Crédit' / 'Débit') est requise."], 0, empty_stats

    valid_rows = []
    duplicate_rows = []
    seen_in_batch = set()

    # Empreintes des opérations existantes pour le contrôle des doublons
    if existing_df is None:
        try:
            existing_df = load_transactions()
        except Exception:
            existing_df = pd.DataFrame()

    existing_signatures = set()
    if existing_df is not None and not existing_df.empty:
        for _, r in existing_df.iterrows():
            d_str = str(r.get("date", ""))
            t_str = str(r.get("type", ""))
            m_val = r.get("montant", 0.0)
            l_str = str(r.get("libelle", ""))
            p_str = str(r.get("partenaire", ""))
            sig = compute_operation_signature(d_str, t_str, m_val, l_str, p_str)
            existing_signatures.add(sig)

    today = get_today_morocco()

    for index, row in raw_df.iterrows():
        line_num = index + 2
        
        # 1. Date opération
        raw_date = row.get("date")
        try:
            parsed_date = pd.to_datetime(raw_date, format="mixed", dayfirst=True)
            if pd.isna(parsed_date):
                errors.append(f"Ligne {line_num} : Date opération invalide ({raw_date}).")
                continue
            date_str = parsed_date.strftime("%Y-%m-%d")
        except Exception:
            errors.append(f"Ligne {line_num} : Format de date non reconnu ({raw_date}).")
            continue

        # 2. Date échéance
        raw_ech = row.get("date_echeance")
        try:
            if pd.notna(raw_ech):
                ech_parsed = pd.to_datetime(raw_ech, format="mixed", dayfirst=True)
                ech_str = ech_parsed.strftime("%Y-%m-%d")
            else:
                ech_str = date_str
        except Exception:
            ech_str = date_str

        # 3. Montants et Type si format Crédit / Débit séparé
        forced_type = None
        raw_ttc = row.get("montant")
        raw_ht = row.get("montant_ht")

        if "col_credit" in row and "col_debit" in row:
            try:
                c_val = float(str(row.get("col_credit", 0)).replace("DH", "").replace("MAD", "").replace(" ", "").replace(",", ".")) if pd.notna(row.get("col_credit")) else 0.0
            except Exception:
                c_val = 0.0
            try:
                d_val = float(str(row.get("col_debit", 0)).replace("DH", "").replace("MAD", "").replace(" ", "").replace(",", ".")) if pd.notna(row.get("col_debit")) else 0.0
            except Exception:
                d_val = 0.0

            if c_val > 0 and d_val == 0:
                raw_ttc = c_val
                forced_type = "Encaissement"
            elif d_val > 0 and c_val == 0:
                raw_ttc = d_val
                forced_type = "Décaissement"
            elif c_val > 0:
                raw_ttc = c_val
                forced_type = "Encaissement"

        raw_taux = row.get("taux_tva", 20.0)

        try:
            taux_val = float(str(raw_taux).replace("%", "").replace(",", ".")) if pd.notna(raw_taux) else 20.0
        except Exception:
            taux_val = 20.0

        ht_val = None
        ttc_val = None

        try:
            if pd.notna(raw_ht):
                cleaned_ht = str(raw_ht).replace("DH", "").replace("MAD", "").replace(" ", "").replace(",", ".")
                ht_val = abs(float(cleaned_ht))
        except Exception:
            pass

        try:
            if pd.notna(raw_ttc):
                cleaned_ttc = str(raw_ttc).replace("DH", "").replace("MAD", "").replace(" ", "").replace(",", ".")
                ttc_val = abs(float(cleaned_ttc))
        except Exception:
            pass

        if ht_val is None and ttc_val is None:
            errors.append(f"Ligne {line_num} : Montant introuvable ou non numérique.")
            continue

        ht_calc, taux_calc, tva_calc, ttc_calc = compute_tva_amounts(
            montant_ht=ht_val, taux_tva=taux_val, montant_ttc=ttc_val
        )

        if ttc_calc <= 0:
            errors.append(f"Ligne {line_num} : Montant nul ou négatif.")
            continue

        # 4. Libellé, Partenaire & Catégorie
        libelle_val = str(row.get("libelle", f"Opération {date_str}")).strip()
        if not libelle_val or libelle_val == "nan":
            libelle_val = f"Opération {date_str}"

        partenaire_val = str(row.get("partenaire", "Divers")).strip()
        if not partenaire_val or partenaire_val == "nan":
            partenaire_val = "Divers"

        cat_raw = str(row.get("categorie", "")).strip()
        cat_val = cat_raw if cat_raw and cat_raw != "nan" else ""

        # 5. Détermination rigoureuse du Type (Encaissement vs Décaissement)
        if forced_type:
            type_val = forced_type
        else:
            raw_type_field = row.get("type")
            raw_montant_orig = row.get("montant", ttc_calc)
            type_val = resolve_operation_type(
                raw_type_val=raw_type_field,
                libelle=libelle_val,
                montant=raw_montant_orig,
                categorie=cat_val
            )

        # Complétion de la catégorie PCGE si absente
        if not cat_val:
            if type_val == "Encaissement":
                cat_val = "Ventes de marchandises au Maroc (Cte 7111)"
            else:
                cat_val = "Fournisseurs & Achats de marchandises / matières (Cte 611/612)"

        statut_raw = str(row.get("statut", "Réalisé")).strip().lower()
        statut_val = "Prévu" if ("prevu" in statut_raw or "prévu" in statut_raw) else "Réalisé"

        # Statut paiement
        if statut_val == "Réalisé":
            statut_p = "Payé"
        else:
            statut_p = "En retard" if ech_str < today.strftime("%Y-%m-%d") else "En attente"

        comment_val = str(row.get("commentaire", "Importation")).strip()
        if comment_val == "nan":
            comment_val = ""

        # 6. Détection et filtrage des doublons stricts
        sig = compute_operation_signature(date_str, type_val, ttc_calc, libelle_val, partenaire_val)
        is_duplicate = (sig in seen_in_batch) or (sig in existing_signatures)

        op_data = {
            "id": str(uuid.uuid4())[:8],
            "date": date_str,
            "date_echeance": ech_str,
            "libelle": libelle_val,
            "type": type_val,
            "categorie": cat_val,
            "partenaire": partenaire_val,
            "montant_ht": ht_calc,
            "taux_tva": taux_calc,
            "montant_tva": tva_calc,
            "montant": ttc_calc,
            "statut": statut_val,
            "statut_paiement": statut_p,
            "commentaire": comment_val
        }

        if is_duplicate:
            duplicate_rows.append(op_data)
        else:
            seen_in_batch.add(sig)
            valid_rows.append(op_data)

    df_valid = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame(columns=REQUIRED_COLUMNS)
    duplicates_count = len(duplicate_rows)

    nb_enc = int((df_valid["type"] == "Encaissement").sum()) if not df_valid.empty else 0
    tot_enc = float(df_valid[df_valid["type"] == "Encaissement"]["montant"].sum()) if not df_valid.empty else 0.0
    nb_dec = int((df_valid["type"] == "Décaissement").sum()) if not df_valid.empty else 0
    tot_dec = float(df_valid[df_valid["type"] == "Décaissement"]["montant"].sum()) if not df_valid.empty else 0.0

    stats = {
        "total_lignes": len(raw_df),
        "nb_valides": len(df_valid),
        "nb_encaissements": nb_enc,
        "total_encaissements": tot_enc,
        "nb_decaissements": nb_dec,
        "total_decaissements": tot_dec,
        "nb_doublons": duplicates_count,
        "nb_rejetes": len(errors),
        "duplicate_rows": duplicate_rows
    }

    return df_valid, errors, duplicates_count, stats
