"""
Module d'importation, de validation et de traitement des opérations comptables pour SmartCash AI.
Prend en charge les formats CSV et Excel (.xlsx).
"""

import io
import re
import unicodedata
import pandas as pd
import numpy as np

def normaliser_chaine(texte):
    """Supprime les accents, met en minuscules et élimine les caractères spéciaux."""
    if not isinstance(texte, str):
        return ""
    texte = unicodedata.normalize('NFD', texte)
    texte = "".join([c for c in texte if unicodedata.category(c) != 'Mn'])
    texte = texte.lower().strip()
    texte = re.sub(r'[\s\-_/\.]+', '_', texte)
    return texte

# Listes de synonymes pour la détection automatique des colonnes
CANDIDATS_DATE = [
    'date', 'date_op', 'date_operation', 'date_d_operation', 'date_mouvement',
    'date_valeur', 'jour', 'periode', 'dt', 'date_effet'
]

CANDIDATS_LIBELLE = [
    'libelle', 'libelle_operation', 'designation', 'description', 'motif',
    'operation', 'intitule', 'texte', 'detail', 'details', 'commentaire', 'tiers'
]

CANDIDATS_TYPE = [
    'type', 'type_op', 'type_operation', 'sens', 'nature', 'mouvement',
    'categorie', 'flux', 'sens_mouvement', 'sens_operation', 'credit_debit'
]

CANDIDATS_MONTANT = [
    'montant', 'montant_dh', 'montant_mad', 'montant_ttc', 'valeur', 'total',
    'somme', 'prix', 'debit_credit', 'solde_mouvement'
]

def detecter_colonnes(colonnes):
    """
    Identifie automatiquement les colonnes pour Date, Libellé, Type et Montant.
    Retourne un dictionnaire avec les noms exacts trouvés ou None.
    """
    mapping = {
        'date': None,
        'libelle': None,
        'type': None,
        'montant': None
    }
    
    colonnes_norm = {col: normaliser_chaine(str(col)) for col in colonnes}
    
    # 1. Date
    for orig, norm in colonnes_norm.items():
        if norm in CANDIDATS_DATE or any(c in norm for c in ['date', 'jour']):
            mapping['date'] = orig
            break
            
    # 2. Libellé
    for orig, norm in colonnes_norm.items():
        if orig != mapping['date'] and (norm in CANDIDATS_LIBELLE or any(c in norm for c in ['libelle', 'designation', 'description'])):
            mapping['libelle'] = orig
            break
            
    # 3. Type
    for orig, norm in colonnes_norm.items():
        if orig not in [mapping['date'], mapping['libelle']] and (norm in CANDIDATS_TYPE or any(c in norm for c in ['type', 'sens', 'nature'])):
            mapping['type'] = orig
            break
            
    # 4. Montant
    for orig, norm in colonnes_norm.items():
        if orig not in [mapping['date'], mapping['libelle'], mapping['type']] and (norm in CANDIDATS_MONTANT or any(c in norm for c in ['montant', 'valeur', 'total'])):
            mapping['montant'] = orig
            break
            
    return mapping

def normaliser_type_operation(valeur):
    """
    Normalise le type d'opération en 'Encaissement' ou 'Décaissement'.
    Retourne None si la valeur n'est pas reconnue.
    """
    if pd.isna(valeur):
        return None
    val_str = normaliser_chaine(str(valeur))
    
    # Encaissement
    if any(k in val_str for k in ['encaissement', 'credit', 'entree', 'recette', 'gain', 'versement', 'inflow', 'client']) or val_str == '+':
        return 'Encaissement'
        
    # Décaissement
    if any(k in val_str for k in ['decaissement', 'debit', 'sortie', 'depense', 'charge', 'retrait', 'outflow', 'fournisseur', 'frais', 'salaire']) or val_str == '-':
        return 'Décaissement'
        
    return None

def convertir_montant(valeur):
    """
    Convertit une valeur brute en float positif.
    Retourne (montant, erreur)
    """
    if pd.isna(valeur):
        return None, "Valeur manquante"
        
    if isinstance(valeur, (int, float)):
        if np.isnan(valeur):
            return None, "Valeur manquante"
        return abs(float(valeur)), None
        
    val_str = str(valeur).strip()
    # Nettoyage des devises et espaces
    val_str = re.sub(r'[^\d,\.\-\+]', '', val_str)
    
    if not val_str:
        return None, "Montant vide ou non numérique"
        
    # Si virgule utilisée comme séparateur décimal (ex: 1 250,50)
    if ',' in val_str and '.' in val_str:
        # Format européen 1.250,50 -> 1250.50
        if val_str.rfind(',') > val_str.rfind('.'):
            val_str = val_str.replace('.', '').replace(',', '.')
        else:
            val_str = val_str.replace(',', '')
    elif ',' in val_str:
        val_str = val_str.replace(',', '.')
        
    try:
        montant = float(val_str)
        return abs(montant), None
    except ValueError:
        return None, f"Valeur non numérique : '{valeur}'"

def valider_et_traiter_operations(df_source, col_date, col_libelle, col_type, col_montant):
    """
    Valide ligne par ligne le jeu de données importé.
    Ne remplace pas silencieusement les données invalides par zéro.
    Retourne (df_valide, erreurs_trouvees, stats_validation).
    """
    erreurs = []
    lignes_valides = []
    
    total_lignes = len(df_source)
    
    for idx, row in df_source.iterrows():
        num_ligne = idx + 2  # Numérotation naturelle façon tableur (ligne 1 = en-tête)
        ligne_a_erreur = False
        
        # 1. Date
        date_raw = row.get(col_date)
        if pd.isna(date_raw):
            erreurs.append(f"Ligne {num_ligne} : Date manquante.")
            ligne_a_erreur = True
            date_clean = None
        elif isinstance(date_raw, (pd.Timestamp, pd.DatetimeIndex)):
            date_clean = pd.to_datetime(date_raw)
        else:
            date_str = str(date_raw).strip()
            date_clean = None
            # Essayer d'abord le format ISO AAAA-MM-JJ ou timestamp
            try:
                date_clean = pd.to_datetime(date_str, format="%Y-%m-%d")
            except Exception:
                try:
                    date_clean = pd.to_datetime(date_str, format="%d/%m/%Y")
                except Exception:
                    try:
                        date_clean = pd.to_datetime(date_str, dayfirst=True)
                    except Exception:
                        erreurs.append(f"Ligne {num_ligne} : Format de date non reconnu ('{date_raw}'). Utilisez JJ/MM/AAAA ou AAAA-MM-JJ.")
                        ligne_a_erreur = True
                    
        # 2. Libellé
        libelle_raw = row.get(col_libelle)
        if pd.isna(libelle_raw) or str(libelle_raw).strip() == "":
            libelle_clean = f"Opération {idx + 1}"
        else:
            libelle_clean = str(libelle_raw).strip()
            
        # 3. Type
        type_raw = row.get(col_type)
        type_clean = normaliser_type_operation(type_raw)
        if type_clean is None:
            erreurs.append(f"Ligne {num_ligne} : Type d'opération inconnu ('{type_raw}'). Indiquez 'Encaissement' ou 'Décaissement'.")
            ligne_a_erreur = True
            
        # 4. Montant
        montant_raw = row.get(col_montant)
        montant_clean, err_montant = convertir_montant(montant_raw)
        if err_montant:
            erreurs.append(f"Ligne {num_ligne} : Montant invalide ({err_montant}).")
            ligne_a_erreur = True
            
        if not ligne_a_erreur:
            lignes_valides.append({
                'Date': date_clean,
                'Libellé': libelle_clean,
                'Type': type_clean,
                'Montant': montant_clean
            })
            
    df_valide = pd.DataFrame(lignes_valides)
    if not df_valide.empty:
        df_valide = df_valide.sort_values('Date').reset_index(drop=True)
        
    stats = {
        'total_lignes': total_lignes,
        'lignes_valides': len(lignes_valides),
        'nb_erreurs': len(erreurs)
    }
    
    return df_valide, erreurs, stats

def calculer_solde_cumule(df_operations, solde_initial=None):
    """
    Ajoute le solde cumulé chronologique à chaque opération.
    """
    if df_operations.empty:
        return df_operations
        
    df = df_operations.sort_values('Date').copy().reset_index(drop=True)
    
    if solde_initial is not None:
        solde_courant = float(solde_initial)
        soldes_cumules = []
        for _, row in df.iterrows():
            if row['Type'] == 'Encaissement':
                solde_courant += row['Montant']
            else:
                solde_courant -= row['Montant']
            soldes_cumules.append(round(solde_courant, 2))
        df['Solde_Cumule_DH'] = soldes_cumules
    else:
        df['Solde_Cumule_DH'] = None
        
    return df

def generer_donnees_demo_operations():
    """
    Génère un jeu de données réaliste d'opérations quotidiennes d'une PME marocaine
    sur 2 mois (Janvier - Février 2026).
    """
    operations = [
        {"Date": "2026-01-02", "Libellé": "Règlement Client Atlas Industrie SARL", "Type": "Encaissement", "Montant": 48500.0},
        {"Date": "2026-01-05", "Libellé": "Paiement Fournisseur Plastique Maroc", "Type": "Décaissement", "Montant": 31200.0},
        {"Date": "2026-01-07", "Libellé": "Frais de transport & logistique CTM", "Type": "Décaissement", "Montant": 3800.0},
        {"Date": "2026-01-10", "Libellé": "Règlement Client Maghreb Distribution", "Type": "Encaissement", "Montant": 64000.0},
        {"Date": "2026-01-14", "Libellé": "Achat fournitures d'emballage", "Type": "Décaissement", "Montant": 7600.0},
        {"Date": "2026-01-15", "Libellé": "Salaires nets du personnel (Virements)", "Type": "Décaissement", "Montant": 39500.0},
        {"Date": "2026-01-18", "Libellé": "Cotisations CNSS & AMO Maroc", "Type": "Décaissement", "Montant": 12800.0},
        {"Date": "2026-01-20", "Libellé": "Loyer bureaux et entrepôt Sidi Maarouf", "Type": "Décaissement", "Montant": 14000.0},
        {"Date": "2026-01-23", "Libellé": "Règlement Client Tanger Export SA", "Type": "Encaissement", "Montant": 52000.0},
        {"Date": "2026-01-26", "Libellé": "Facture électricité Lydec & Télécoms", "Type": "Décaissement", "Montant": 5400.0},
        {"Date": "2026-01-28", "Libellé": "Remboursement de crédit TVA", "Type": "Encaissement", "Montant": 18500.0},
        {"Date": "2026-01-30", "Libellé": "Paiement Fournisseur Maintenance Machines", "Type": "Décaissement", "Montant": 8900.0},
        {"Date": "2026-02-02", "Libellé": "Règlement Client Fès Emballages", "Type": "Encaissement", "Montant": 41000.0},
        {"Date": "2026-02-05", "Libellé": "Paiement Fournisseur Résines Chimiques", "Type": "Décaissement", "Montant": 29500.0},
        {"Date": "2026-02-09", "Libellé": "Règlement Client Agadir Agro", "Type": "Encaissement", "Montant": 58000.0},
        {"Date": "2026-02-12", "Libellé": "Carburant flotte commerciale Afriquia", "Type": "Décaissement", "Montant": 4200.0},
        {"Date": "2026-02-15", "Libellé": "Salaires nets du personnel (Virements)", "Type": "Décaissement", "Montant": 39500.0},
        {"Date": "2026-02-18", "Libellé": "Cotisations CNSS & AMO Maroc", "Type": "Décaissement", "Montant": 12800.0},
        {"Date": "2026-02-20", "Libellé": "Loyer bureaux et entrepôt", "Type": "Décaissement", "Montant": 14000.0},
        {"Date": "2026-02-24", "Libellé": "Règlement Client Rabat Plast SARL", "Type": "Encaissement", "Montant": 46000.0},
        {"Date": "2026-02-27", "Libellé": "Assurance multirisque professionnelle Wafa", "Type": "Décaissement", "Montant": 6500.0}
    ]
    return pd.DataFrame(operations)

def generer_modele_csv():
    """Génère le contenu binaire d'un modèle CSV type."""
    df_modele = generer_donnees_demo_operations().head(6)
    return df_modele.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')

def generer_modele_excel():
    """Génère le contenu binaire d'un modèle Excel (.xlsx) type."""
    df_modele = generer_donnees_demo_operations().head(6)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df_modele.to_excel(writer, index=False, sheet_name='Operations_Tresorerie')
    return buf.getvalue()
