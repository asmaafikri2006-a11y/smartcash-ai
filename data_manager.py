"""
SmartCash AI - Gestionnaire de Données Financières (Adaptation Maroc 🇲🇦)
Module data_manager.py
Prend en charge le contexte marocain (MAD / DH), fuseau Africa/Casablanca,
PCGE marocain, gestion de la TVA marocaine (20%, 14%, 10%, 7%, 0%),
suivi des factures (HT, TVA, TTC, Échéances, Créances & Dettes) et persistance locale.
"""

import os
import io
import uuid
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
            "Date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
            "Date Échéance": (today + timedelta(days=25)).strftime("%Y-%m-%d"),
            "Libellé": "Facture client OCP Solutions #FC-2026-081",
            "Type": "Encaissement",
            "Catégorie": "Ventes de marchandises au Maroc (Cte 7111)",
            "Partenaire": "Groupe OCP",
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
            "Date Échéance": (today + timedelta(days=28)).strftime("%Y-%m-%d"),
            "Libellé": "Facture SNTL Logistique & Fret #FF-592",
            "Type": "Décaissement",
            "Catégorie": "Transports de marchandises & Déplacements (Cte 6142/6143)",
            "Partenaire": "SNTL Transport",
            "Montant HT": 8500.00,
            "Taux TVA (%)": 14.0,
            "Montant TVA": 1190.00,
            "Montant TTC (DH)": 9690.00,
            "Statut": "Réalisé",
            "Statut Paiement": "Payé",
            "Commentaire": "Frais de transport inter-villes Maroc"
        },
        {
            "Date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
            "Date Échéance": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
            "Libellé": "Loyer commercial siège Casablanca",
            "Type": "Décaissement",
            "Catégorie": "Loyers commerciaux & Charges locatives (Cte 6131)",
            "Partenaire": "Bailleur Anfa",
            "Montant HT": 18500.00,
            "Taux TVA (%)": 0.0,
            "Montant TVA": 0.00,
            "Montant TTC (DH)": 18500.00,
            "Statut": "Prévu",
            "Statut Paiement": "En attente",
            "Commentaire": "Chèque de loyer à émettre"
        },
        {
            "Date": (today + timedelta(days=15)).strftime("%Y-%m-%d"),
            "Date Échéance": (today + timedelta(days=15)).strftime("%Y-%m-%d"),
            "Libellé": "Facture client Marjane Holding #FC-2026-094",
            "Type": "Encaissement",
            "Catégorie": "Ventes de marchandises au Maroc (Cte 7111)",
            "Partenaire": "Marjane Holding",
            "Montant HT": 72000.00,
            "Taux TVA (%)": 20.0,
            "Montant TVA": 14400.00,
            "Montant TTC (DH)": 86400.00,
            "Statut": "Prévu",
            "Statut Paiement": "En attente",
            "Commentaire": "Encaissement traite bancaire prévu"
        }
    ]
    df_template = pd.DataFrame(sample_rows)
    df_template.to_csv(TEMPLATE_CSV, index=False, encoding="utf-8-sig")
    
    try:
        with pd.ExcelWriter(TEMPLATE_XLSX, engine="openpyxl") as writer:
            df_template.to_excel(writer, sheet_name="Operations_Maroc", index=False)
    except Exception:
        pass

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

def parse_and_validate_import(file_buffer, filename: str):
    """
    Lit un fichier importé (.csv ou .xlsx), détecte les colonnes de manière souple
    (y compris HT, TVA, TTC, Échéance, Partenaire), valide les montants et détecte les doublons.
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
            return None, ["Format de fichier non pris en charge. Veuillez utiliser un fichier .csv ou .xlsx."], 0
    except Exception as e:
        return None, [f"Erreur lors de la lecture du fichier : {str(e)}"], 0

    if raw_df.empty:
        return None, ["Le fichier importé est vide."], 0

    # Normalisation souple des noms de colonnes
    col_mapping = {}
    for col in raw_df.columns:
        norm = str(col).lower().strip().replace(" ", "_").replace("é", "e").replace("è", "e").replace("ê", "e")
        if "echeance" in norm or "date_limite" in norm or "due_date" in norm:
            col_mapping[col] = "date_echeance"
        elif "date" in norm:
            col_mapping[col] = "date"
        elif "partenaire" in norm or "client" in norm or "fournisseur" in norm or "tiers" in norm:
            col_mapping[col] = "partenaire"
        elif "ht" in norm and "taux" not in norm and "tva" not in norm:
            col_mapping[col] = "montant_ht"
        elif "taux" in norm and "tva" in norm:
            col_mapping[col] = "taux_tva"
        elif "montant_tva" in norm or "valeur_tva" in norm:
            col_mapping[col] = "montant_tva"
        elif "ttc" in norm or "total" in norm or "montant" in norm or "valeur" in norm:
            col_mapping[col] = "montant"
        elif "libelle" in norm or "desc" in norm or "titre" in norm or "nom" in norm:
            col_mapping[col] = "libelle"
        elif "type" in norm or "sens" in norm:
            col_mapping[col] = "type"
        elif "cat" in norm:
            col_mapping[col] = "categorie"
        elif "statut_paiement" in norm or "etat_paiement" in norm:
            col_mapping[col] = "statut_paiement"
        elif "statut" in norm or "etat" in norm:
            col_mapping[col] = "statut"
        elif "comment" in norm or "note" in norm:
            col_mapping[col] = "commentaire"

    raw_df = raw_df.rename(columns=col_mapping)

    # Vérification des colonnes minimales indispensables
    if "date" not in raw_df.columns:
        return None, ["La colonne 'Date' est obligatoire."], 0
    if "montant" not in raw_df.columns and "montant_ht" not in raw_df.columns:
        return None, ["Au moins une colonne de montant ('Montant TTC' ou 'Montant HT') est requise."], 0

    valid_rows = []
    duplicates_count = 0
    existing_df = load_transactions()
    existing_signatures = set()
    for _, row in existing_df.iterrows():
        sig = f"{row['date']}_{row['libelle']}_{row['montant']}"
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

        # 3. Montants HT, TVA, TTC
        raw_ttc = row.get("montant")
        raw_ht = row.get("montant_ht")
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

        # 4. Type (Encaissement / Décaissement)
        raw_type = str(row.get("type", "")).strip().lower()
        if any(w in raw_type for w in ["encaissement", "recette", "revenu", "credit", "in", "client"]):
            type_val = "Encaissement"
        elif any(w in raw_type for w in ["decaissement", "depense", "charge", "debit", "out", "fournisseur"]):
            type_val = "Décaissement"
        else:
            type_val = "Décaissement" if str(row.get("montant", "")).startswith("-") else "Encaissement"

        # 5. Catégorie & Partenaire
        cat_val = str(row.get("categorie", "")).strip()
        if not cat_val or cat_val == "nan":
            cat_val = "Prestations de services & Produits d'exploitation (Cte 712)" if type_val == "Encaissement" else "Autres charges externes d'exploitation"

        partenaire_val = str(row.get("partenaire", "Divers")).strip()
        if not partenaire_val or partenaire_val == "nan":
            partenaire_val = "Divers"

        libelle_val = str(row.get("libelle", f"Opération {date_str}")).strip()
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

        # Détection doublon
        sig = f"{date_str}_{libelle_val}_{ttc_calc}"
        if sig in existing_signatures:
            duplicates_count += 1

        valid_rows.append({
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
        })

    df_valid = pd.DataFrame(valid_rows)
    return df_valid, errors, duplicates_count
