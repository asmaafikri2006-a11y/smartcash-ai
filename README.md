# SmartCash AI — Gestion et Prévision de Trésorerie

Bienvenue dans **SmartCash AI**, une application professionnelle de gestion et de prévision de trésorerie conçue pour les PME et les gestionnaires financiers au Maroc.

L'application utilise un **design professionnel clair** (fond gris perle `#F1F5F9`, cartes blanches `#FFFFFF`, bleu marine `#17365D`, turquoise `#087F8C`), gère l'**importation directe de fichiers Excel (.xlsx) et CSV**, calcule automatiquement le solde cumulé ligne par ligne et propose des **recommandations financières chiffrées**.

---

## 🌟 Organisation du Tableau de Bord (5 Sections Claires)

1. **📥 1. Importer les opérations comptables :**
   - Importation glisser-déposer de fichiers **CSV** ou **Excel (.xlsx)** via `st.file_uploader`.
   - Détection automatique et intelligente des colonnes (`Date`, `Libellé`, `Type`, `Montant`) avec tolérance aux accents et variations de casse.
   - Boutons de téléchargement de **modèles prêts à l'emploi (CSV et Excel)**.
   - Bouton de chargement immédiat des **données de démonstration**.
   - Contrôle d'intégrité strict : signalement précis des anomalies (dates illisibles, montants non numériques) sans remplacement silencieux par zéro.
   - Réinitialisation propre à chaque nouveau fichier importé.

2. **📊 2. Indicateurs financiers :**
   - **Solde Initial** saisi par l'utilisateur (avec option solde inconnu).
   - **Total des Encaissements** (entrées de fonds).
   - **Total des Décaissements** (sorties de fonds).
   - **Solde Net de la Période** (Encaissements − Décaissements).
   - **Solde Final Calculé** (Solde Initial + Solde Net) avec code couleur (Turquoise favorable, Orange vigilance, Rouge risque de découvert).
   - Formatage strict en Dirhams marocains : exemple `25 000,00 DH`.

3. **📋 3. Tableau des opérations :**
   - Tri chronologique automatique par date.
   - Calcul du **solde cumulé au fil de l'eau** pour chaque opération.
   - Filtre par type (Tous, Encaissements, Décaissements) et recherche textuelle.
   - Exportation des opérations traitées et nettoyées au format CSV.

4. **📈 4. Graphiques d'analyse :**
   - **Évolution de la trésorerie dans le temps** : courbe fluide du solde cumulé avec ligne de découvert à 0 DH (rouge) et seuil de sécurité (orange).
   - **Encaissements vs Décaissements** : diagramme circulaire clair des flux.

5. **💡 5. Prévisions et recommandations :**
   - **Analyse et recommandations concrètes** : alerte de baisse de trésorerie, détection de périodes à découvert, actions concrètes (relance clients, étalement fournisseurs, arbitrage de charges).
   - **Modélisation Machine Learning (Ridge)** : projections prudentes à 3 mois distinguant rigoureusement les calculs comptables et les projections IA.

---

## 📁 Structure du Projet

```text
SmartCashAI/
│
├── app.py                     # Application principale Streamlit (Design clair & Dashboard)
├── data_importer.py           # Moteur d'importation, validation et modèles CSV/Excel
├── ml_model.py                # Modèle de Machine Learning (Ridge Regression & métriques)
├── data_generator.py          # Génération des séries chronologiques de référence
├── test_smartcash.py          # Suite de tests automatiques (CSV, Excel, anomalies, calculs)
├── requirements.txt           # Dépendances (streamlit, pandas, openpyxl, plotly, scikit-learn)
├── lancer_app.bat             # Lanceur Windows automatique (1 double-clic)
├── historique_tresorerie.csv  # Données historiques 24 mois
├── .streamlit/
│   └── config.toml            # Thème clair natif Streamlit (#F1F5F9, #FFFFFF, #17365D)
└── README.md                  # Ce guide explicatif en français
```

---

## 🚀 Comment Lancer l'Application

### Méthode 1 : En un double-clic (Recommandé) ⚡
1. Ouvrez le dossier `SmartCashAI`.
2. Double-cliquez sur `lancer_app.bat`.
3. L'application s'ouvre automatiquement dans votre navigateur web à l'adresse `http://localhost:8501`.

### Méthode 2 : Via le Terminal PowerShell 💻
```powershell
cd C:\Users\Hp\Desktop\am\SmartCashAI
pip install -r requirements.txt
streamlit run app.py
```

---

## 🧪 Comment Lancer les Tests Automatiques

Une suite de tests a été intégrée pour valider le bon fonctionnement de tous les cas d'usage :
```powershell
cd C:\Users\Hp\Desktop\am\SmartCashAI
python test_smartcash.py
```

Les 4 tests suivants sont exécutés :
1. ✅ **Test 1 : Import d'un fichier CSV valide**
2. ✅ **Test 2 : Import d'un fichier Excel (.xlsx) valide**
3. ✅ **Test 3 : Détection d'un fichier mal formaté** (dates erronées, montants texte, types inconnus — vérifie qu'aucune donnée invalide n'est remplacée par zéro)
4. ✅ **Test 4 : Cas sans fichier & calcul arithmétique exact du solde cumulé**
