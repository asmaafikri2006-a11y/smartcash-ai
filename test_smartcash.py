"""
Tests de validation pour SmartCash AI :
1. Fichier CSV valide
2. Fichier Excel (.xlsx) valide
3. Fichier mal formaté (erreurs de date, montant non numérique, types invalides)
4. Cas sans fichier (chargement données de démonstration)
5. Calculs comptables et cumulatifs
"""

import io
import pandas as pd
import numpy as np
import data_importer
from ml_model import ModelePrevisionTresorerie

def test_csv_valide():
    print("--- Test 1 : CSV valide ---")
    csv_bytes = data_importer.generer_modele_csv()
    df_raw = pd.read_csv(io.BytesIO(csv_bytes), sep=';', encoding='utf-8-sig')
    
    mapping = data_importer.detecter_colonnes(df_raw.columns)
    assert mapping['date'] is not None, "Date non détectée"
    assert mapping['libelle'] is not None, "Libellé non détecté"
    assert mapping['type'] is not None, "Type non détecté"
    assert mapping['montant'] is not None, "Montant non détecté"
    
    df_valide, errs, stats = data_importer.valider_et_traiter_operations(
        df_raw, mapping['date'], mapping['libelle'], mapping['type'], mapping['montant']
    )
    assert stats['lignes_valides'] == len(df_raw), f"Lignes attendues {len(df_raw)}, obtenues {stats['lignes_valides']}"
    assert len(errs) == 0, f"Erreurs inattendues : {errs}"
    print(f"OK : {stats['lignes_valides']} lignes validées sans erreur.")

def test_excel_valide():
    print("--- Test 2 : Excel (.xlsx) valide ---")
    xlsx_bytes = data_importer.generer_modele_excel()
    df_raw = pd.read_excel(io.BytesIO(xlsx_bytes), engine='openpyxl')
    
    mapping = data_importer.detecter_colonnes(df_raw.columns)
    assert mapping['date'] is not None, "Date non détectée dans Excel"
    assert mapping['libelle'] is not None, "Libellé non détecté dans Excel"
    assert mapping['type'] is not None, "Type non détecté dans Excel"
    assert mapping['montant'] is not None, "Montant non détecté dans Excel"
    
    df_valide, errs, stats = data_importer.valider_et_traiter_operations(
        df_raw, mapping['date'], mapping['libelle'], mapping['type'], mapping['montant']
    )
    assert stats['lignes_valides'] == len(df_raw)
    assert len(errs) == 0
    print(f"OK : Excel {stats['lignes_valides']} lignes validées avec succès.")

def test_fichier_mal_formate():
    print("--- Test 3 : Fichier mal formaté (erreurs contrôlées) ---")
    # Création délibérée d'anomalies
    bad_data = pd.DataFrame([
        {"Date_Op": "2026-01-02", "Designation": "Opération OK", "Sens": "Encaissement", "Valeur": "15000"},
        {"Date_Op": "date_invalide_99/99", "Designation": "Mauvaise date", "Sens": "Encaissement", "Valeur": "5000"},
        {"Date_Op": "2026-01-04", "Designation": "Montant texte", "Sens": "Décaissement", "Valeur": "abc_invalide"},
        {"Date_Op": "2026-01-05", "Designation": "Type inconnu", "Sens": "Inconnu_XYZ", "Valeur": "8000"},
        {"Date_Op": None, "Designation": "Ligne vide", "Sens": None, "Valeur": None}
    ])
    
    mapping = data_importer.detecter_colonnes(bad_data.columns)
    df_valide, errs, stats = data_importer.valider_et_traiter_operations(
        bad_data, mapping['date'], mapping['libelle'], mapping['type'], mapping['montant']
    )
    
    # 1 seule ligne est 100% valide (la première)
    assert stats['lignes_valides'] == 1, f"Attendu 1 ligne valide, obtenu {stats['lignes_valides']}"
    assert len(errs) >= 4, f"Attendu au moins 4 erreurs explicites, obtenu {len(errs)}"
    
    # Vérification que le montant de la ligne 3 n'a PAS été remplacé silencieusement par 0
    # La ligne invalide doit être rejetée et listée dans errs
    assert any("abc_invalide" in e or "non numérique" in e for e in errs), "Erreur de montant non détectée !"
    assert any("date_invalide" in e or "non reconnu" in e for e in errs), "Erreur de date non détectée !"
    assert any("Inconnu_XYZ" in e or "Type" in e for e in errs), "Erreur de type non détectée !"
    print(f"OK : {len(errs)} erreurs correctement identifiées et expliquées, données invalides non remplacées par 0.")

def test_cas_sans_fichier_et_cumul():
    print("--- Test 4 : Cas sans fichier & calcul du solde cumulé ---")
    df_demo = data_importer.generer_donnees_demo_operations()
    mapping = data_importer.detecter_colonnes(df_demo.columns)
    df_valide, errs, stats = data_importer.valider_et_traiter_operations(
        df_demo, mapping['date'], mapping['libelle'], mapping['type'], mapping['montant']
    )
    
    solde_init = 50000.0
    df_cum = data_importer.calculer_solde_cumule(df_valide, solde_init)
    
    total_enc = df_valide[df_valide['Type'] == 'Encaissement']['Montant'].sum()
    total_dec = df_valide[df_valide['Type'] == 'Décaissement']['Montant'].sum()
    solde_final_theorique = solde_init + total_enc - total_dec
    
    assert abs(df_cum['Solde_Cumule_DH'].iloc[-1] - solde_final_theorique) < 0.01, "Discordance dans le solde final calculé !"
    print(f"OK : Solde initial ({solde_init}) + Enc ({total_enc}) - Dec ({total_dec}) = {solde_final_theorique} DH parfaitement vérifié.")

if __name__ == "__main__":
    test_csv_valide()
    test_excel_valide()
    test_fichier_mal_formate()
    test_cas_sans_fichier_et_cumul()
    print("\n TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS !")
