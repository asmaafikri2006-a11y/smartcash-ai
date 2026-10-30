# SmartCash AI Maroc 🇲🇦 — Application Intelligente de Prévision de Trésorerie

> **« Votre trésorerie, anticipée intelligemment »**  
> *Projet réalisé dans le cadre du cursus en Gestion Financière et Comptable — Module Intelligence Artificielle.*  
> *Adapté aux pratiques des entreprises marocaines (Plan Comptable Général des Entreprises - PCGE & Code Général des Impôts - CGI).*

---

## 📌 Présentation Générale

**SmartCash AI Maroc** est une solution web décisionnelle de gestion et de prévision de trésorerie conçue spécifiquement pour les entreprises au Maroc. Elle permet aux dirigeants de PME, directeurs administratifs et financiers (DAF) et experts-comptables de piloter leurs liquidités en **Dirhams Marocains (MAD / DH)** et d'anticiper les ruptures de trésorerie grâce au **Machine Learning**.

L'application intègre les spécificités économiques et comptables marocaines :
- **Monnaie par défaut :** Dirham marocain (DH / MAD) avec formatage financier lisible (`15 000,00 DH`).
- **Fuseau horaire :** `Africa/Casablanca` (GMT+1).
- **Pratiques comptables marocaines (PCGE) :** Catégorisation normalisée des flux (ventes locales Cte 7111, export Cte 7113, achats marchandises Cte 611, salaires et CNSS/AMO Cte 617, loyers Cte 6131, etc.).
- **Fiscalité marocaine (TVA CGI) :** Prise en charge des taux de TVA marocains (20%, 14%, 10%, 7%, 0%), calcul automatique et cohérent des montants **HT, TVA et TTC**, et calcul de la position nette de TVA due à la DGI.
- **Pilotage du BFR & Échéances :** Suivi distinct des **créances clients**, des **dettes fournisseurs**, des **échéances de paiement** et des retards.
- **Intelligence Artificielle rigoureuse :** Algorithmes supervisés (Random Forest, Ridge) entraînés sur les séries temporelles pour estimer le flux net et le solde futur avec intervalles de confiance.

---

## 🎨 Nouveau Design Bleu Marine Sombre (*Fintech Dark Navy*)

L'application arbore une identité visuelle moderne et contrastée, évitant tout fond blanc agressif :
- **Fond principal :** Bleu marine sombre `#0B1630`
- **Barre latérale :** Bleu marine nuit `#101F3D`
- **Cartes et panneaux :** Bleu marine intermédiaire `#172A4D` avec bordures `#23385E`
- **Bleu d'accentuation :** `#3B82F6`
- **Typographie :** Blanc cassé `#F1F5F9` et bleu doux `#B7C5DA`
- **Flux positifs & Encaissements :** Vert émeraude `#22C55E`
- **Flux négatifs & Alertes critiques :** Rouge `#EF4444`
- **Avertissements & Échéances :** Ambre / Orange `#F59E0B`
- **Graphiques interactifs Plotly :** Thème sombre assorti avec axes et infobulles libellés en `DH`.

---

## 🏗️ Structure Modulaire du Code

```text
SmartCash AI/
├── app.py                      # Interface Streamlit avec thème Dark Navy et navigation
├── financial_calculations.py   # Calculs des soldes en DH, créances/dettes, ratios BFR, alertes DGI/banque
├── forecast_model.py           # Modèles Scikit-learn (Random Forest, Ridge) et Feature Engineering
├── data_manager.py             # Formatage DH, fuseau Casablanca, TVA marocaine, persistance CSV
├── report_generator.py         # Génération de rapports PDF exécutifs certifiés en DH (fpdf2)
├── sample_data.csv             # Jeu de données marocain (Atlas Distribution SARL - Casablanca)
├── requirements.txt            # Dépendances Python nécessaires
├── lancer_app.bat              # Lanceur Windows en 1 clic
├── README.md                   # Documentation complète et guide de soutenance
├── .streamlit/
│   └── config.toml             # Configuration du thème Streamlit Dark Navy
└── data/
    ├── transactions.csv        # Base locale active des opérations
    ├── sample_data.csv         # Référence des données de démonstration
    ├── modele_smartcash.csv    # Modèle d'importation CSV marocain (avec HT, TVA, TTC)
    └── modele_smartcash.xlsx   # Modèle d'importation Excel marocain
```

---

## 🚀 Lancement Rapide sous Windows

### Option 1 (Double-clic)
Double-cliquez sur **`lancer_app.bat`**. Le serveur Streamlit se lance et ouvre directement votre navigateur :  
👉 **`http://localhost:8501`**

### Option 2 (Invite de commande / PowerShell)
```powershell
python -m streamlit run app.py
```

---

## 🧭 Fonctionnalités par Page

### 1. 📊 Tableau de bord Financier
- **8 Indicateurs clés en Dirhams :**
  1. *Solde Actuel* (disponibilités bancaires en DH).
  2. *Encaissements* (total TTC sur la période).
  3. *Décaissements* (total TTC sur la période).
  4. *Solde Prévisionnel* (projection IA à horizon).
  5. *Créances Clients* (factures clients en attente + montant échu).
  6. *Dettes Fournisseurs* (factures à payer + montant échu).
  7. *Paiements à venir sous 30 jours* (engagements prioritaires).
  8. *Niveau de Risque* (Faible, Modéré, Élevé, Critique).
- **Diagnostic managérial automatique :** Analyse rédigée de la santé de trésorerie en Dirhams.
- **Graphiques Plotly Dark :**
  - Trajectoire du solde (historique réalisé vs prévision IA) avec seuils de découvert (0 DH) et de sécurité.
  - Répartition des dépenses selon la nomenclature PCGE (Donut chart).
  - Comparatif mensuel des encaissements et décaissements en DH.

### 2. 💳 Opérations Financières & Facturation
- **Gestion des factures :** Saisie du Montant Hors Taxes (HT), Taux de TVA (20%, 14%, 10%, 7%, 0%), Montant TVA et Montant TTC.
- **Suivi des tiers :** Nom du client ou du fournisseur marocain (*Partenaire*).
- **Échéancier de paiement :** Suivi des dates d'échéance et détection immédiate des factures en retard de paiement.
- **Code couleur intuitif :** Vert pour les encaissements, Rouge pour les décaissements, badges d'état (Payé, En attente, En retard).
- Recherche instantanée, filtres croisés, modification et suppression en un clic.

### 3. 📥 Importation de Données
- Support des fichiers **Excel (`.xlsx`, `.xls`)** et **CSV (`.csv`)**.
- Reconnaissance intelligente des colonnes : `Date`, `Date Échéance`, `Libellé`, `Partenaire`, `Montant HT`, `Taux TVA`, `Montant TTC`, `Statut`.
- Contrôle de cohérence arithmétique ($TTC = HT + TVA$) et détection des doublons.
- Téléchargement des **modèles Excel et CSV prêts à l'emploi**.

### 4. 🤖 Prévision Intelligente par IA (MAD)
- Horizons de prévision paramétrables : **7, 15 ou 30 jours**.
- Algorithmes : **Random Forest Regressor** ou **Régression Ridge**.
- Intervalles d'incertitude statistiques à 80% projetés en DH.
- Évaluation sur échantillon test réel : **MAE en Dirhams**, **RMSE** et **score $R^2$**.
- Importance des variables explicatives : impact du rythme hebdomadaire, des échéances fiscales (TVA le 20, salaires le 28, CNSS le 10).
- Repli transparent sur méthode de référence si les données sont insuffisantes (< 21 jours).

### 5. ⚠️ Alertes & Recommandations (Maroc)
- Détection des tensions de liquidités et recommandations actionnables adaptées à l'environnement marocain :
  - Négociation de facilité de caisse / découvert bancaire.
  - Mobilisation de créances par escompte d'effets de commerce (traites) ou affacturage.
  - Rappel des échéances fiscales DGI (SIMPL-TVA) et sociales (Damancom CNSS/AMO).

### 6. 📈 Analyse & Rapports
- Ratios financiers : *Burn Rate* quotidien en DH, *Runway* (autonomie en jours), ratio de couverture.
- **Position de TVA marocaine :** TVA collectée, TVA déductible et TVA nette due à l'État (DGI).
- **Export PDF Officiel en DH :** Génération d'une synthèse imprimable conforme aux standards bancaires.
- **Export CSV :** Grand livre complet téléchargeable.

### 7. 🧠 Comprendre l'IA (Module Pédagogique)
- Comparaison théorique : Automatisation par règles vs Machine Learning supervisé.
- Justification du choix du Machine Learning tabulaire vs Deep Learning.
- Guide pas-à-pas pour la soutenance orale de 5 minutes.

---

## 🇲🇦 Données de Démonstration : Atlas Distribution SARL

L'application est fournie avec un scénario réaliste d'une PME marocaine basée à Casablanca (136 opérations sur 5 mois) :
- Loyers commerciaux à Casablanca (Ain Sebaâ / Sidi Maârouf).
- Masse salariale et cotisations CNSS / AMO déclarées via Damancom.
- Factures clients auprès de grands comptes marocains (OCP, Marjane, LabelVie, Dislog, Cosumar...).
- Fournisseurs réguliers (SNTL, Lydec, matériel informatique, prestataires web).
- Télérèglements mensuels de TVA à la DGI.

---

## ⚖️ Rigueur & Déontologie

SmartCash AI Maroc est un **outil d'aide à la décision financière et de simulation prédictive**. Il ne prétend pas remplacer un logiciel de comptabilité légale agréé ou le jugement d'un expert-comptable inscrit à l'Ordre des Experts-Comptables du Maroc.
