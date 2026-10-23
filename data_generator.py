"""
Module de génération de données historiques fictives pour SmartCash AI.
Simule 24 mois d'historique de flux de trésorerie pour une PME marocaine (en Dirhams - DH).
"""

import pandas as pd
import numpy as np
import os

MOIS_FR = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}

def generer_donnees_historiques(filepath=None):
    """
    Génère un historique fictif réaliste sur 24 mois (2024-2025)
    en Dirhams marocains (DH).
    """
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), "historique_tresorerie.csv")
        
    np.random.seed(42)
    dates = pd.date_range(start="2024-01-01", periods=24, freq="MS")
    
    data = []
    solde_courant = 75000.0  # Solde initial de départ en DH (Janvier 2024)
    
    for i, date in enumerate(dates):
        month_idx = i + 1
        month_str = date.strftime("%Y-%m")
        mois_libelle = f"{MOIS_FR[date.month]} {date.year}"
        
        # Tendance haussière légère + effet saisonnier
        tendance = 1.0 + (i * 0.012)
        saisonnalite = 1.0 + 0.10 * np.sin(2 * np.pi * (date.month - 1) / 12)
        
        # Encaissements
        reglements_clients = round(float(np.random.normal(135000, 10000) * tendance * saisonnalite), 2)
        autres_encaissements = round(float(np.random.choice([0, 4000, 8000, 12000], p=[0.45, 0.30, 0.15, 0.10])), 2)
        total_encaissements = round(reglements_clients + autres_encaissements, 2)
        
        # Décaissements
        fournisseurs = round(float(np.random.normal(72000, 7000) * tendance), 2)
        salaires_charges = round(float(38000 * (1 + 0.006 * i)), 2)
        loyer_charges = 12000.0  # Loyer et charges fixes stables
        autres_decaissements = round(float(np.random.normal(8500, 1500)), 2)
        total_decaissements = round(fournisseurs + salaires_charges + loyer_charges + autres_decaissements, 2)
        
        flux_net = round(total_encaissements - total_decaissements, 2)
        solde_initial = round(solde_courant, 2)
        solde_final = round(solde_initial + flux_net, 2)
        
        data.append({
            "Mois": month_str,
            "Libelle_Mois": mois_libelle,
            "Mois_Index": month_idx,
            "Solde_Initial_DH": solde_initial,
            "Reglements_Clients_DH": reglements_clients,
            "Autres_Encaissements_DH": autres_encaissements,
            "Total_Encaissements_DH": total_encaissements,
            "Fournisseurs_DH": fournisseurs,
            "Salaires_Charges_DH": salaires_charges,
            "Loyer_Charges_DH": loyer_charges,
            "Autres_Decaissements_DH": autres_decaissements,
            "Total_Decaissements_DH": total_decaissements,
            "Flux_Net_DH": flux_net,
            "Solde_Final_DH": solde_final
        })
        
        solde_courant = solde_final
        
    df = pd.DataFrame(data)
    try:
        df.to_csv(filepath, index=False, encoding="utf-8")
        print(f"Fichier historique généré avec succès : {filepath}")
    except Exception as e:
        print(f"Erreur d'écriture : {e}")
    return df

def charger_ou_generer_donnees(filepath=None):
    """
    Charge les données depuis le fichier CSV s'il existe, sinon les génère.
    """
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), "historique_tresorerie.csv")
        
    if os.path.exists(filepath):
        try:
            return pd.read_csv(filepath, encoding="utf-8")
        except Exception:
            return generer_donnees_historiques(filepath)
    else:
        return generer_donnees_historiques(filepath)

if __name__ == "__main__":
    df = generer_donnees_historiques()
    print(f"Dataset généré avec succès. Aperçu des 3 premiers mois :\n{df.head(3)}")
