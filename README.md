# SmartCash — Prévision de Trésorerie

Bienvenue dans **SmartCash**, une application de tableau de bord financier conçue pour les gestionnaires et étudiants en gestion financière et comptable. 

Elle permet de simuler, prévoir et analyser la trésorerie d'entreprise en **Dirhams marocains (DH)**, tout en intégrant des visualisations interactives adaptées à un environnement sombre professionnel, un modèle de **Machine Learning (Ridge)** et un module d'**analyse et recommandations**.

---

## 🌟 Fonctionnalités Principales

1. **Saisie budgétaire intuitive en Dirhams (DH) :**
   - **Solde initial de trésorerie** disponible en banque et caisse.
   - **Encaissements prévus** : règlements clients attendus et autres encaissements (remboursements TVA, subventions, apports).
   - **Décaissements prévus** : fournisseurs & achats, salaires & charges sociales (CNSS/AMO), loyer & charges locatives, autres dépenses d'exploitation.

2. **Formule financière fondamentale :**
   $$\text{Solde Prévisionnel} = \text{Solde Initial} + \text{Encaissements Prévus} - \text{Décaissements Prévus}$$

3. **Système de Diagnostic et d'Alertes Tricolore :**
   - 🟢 **Vert (Trésorerie Saine)** : Solde supérieur au seuil de sécurité. Conseils pour placer les excédents (DAT, OPCVM) et négocier des escomptes de caisse.
   - 🟠 **Orange (Trésorerie Tendue)** : Solde positif mais faible marge de manœuvre. Conseils sur la relance client, la gestion du DSO et la temporisation des charges.
   - 🔴 **Rouge (Alerte Découvert)** : Déficit de liquidités. Plan d'urgence : mobilisation de créances (escompte commercial, affacturage), négociation de facilité de caisse, étalement des dettes fournisseurs.

4. **Visualisations Graphiques Interactives (Plotly) :**
   - **Graphique en Cascade (Waterfall)** : visualisez étape par étape comment chaque entrée et sortie transforme votre solde initial en solde final.
   - **Répartition des Décaissements** : diagramme circulaire des coûts.

5. **Modélisation par Intelligence Artificielle (Machine Learning) :**
   - Modèle de régression régularisée (**Ridge Regression**) entraîné sur 24 mois d'historique.
   - Projections automatiques des encaissements, décaissements et soldes pour les **3 prochains mois**.
   - Indicateurs de précision du modèle explicités : **$R^2$** (coefficient de détermination) et **MAE** (erreur moyenne absolue en DH).

6. **Données Historiques Fictives & Exportation :**
   - 24 mois de données réalistes d'une PME marocaine.
   - Bouton de téléchargement au format **CSV** pour travailler sur **Excel**.

7. **Guide de l'Étudiant Intégré :**
   - Rappel des notions académiques clés : *FRNG*, *BFR*, *Trésorerie Nette*, différence cruciale entre *Résultat Comptable* et *Trésorerie Réelle*.

---

## 📁 Structure du Projet

```text
SmartCashAI/
│
├── app.py                     # Application principale Streamlit
├── data_generator.py          # Génération et chargement de l'historique fictif (24 mois)
├── ml_model.py                # Modèle de Machine Learning (Ridge Regression, métriques)
├── requirements.txt           # Liste des bibliothèques Python nécessaires
├── lancer_app.bat             # Fichier Windows pour lancer l'application en un double-clic
├── historique_tresorerie.csv  # Fichier CSV contenant les 24 mois d'historique
└── README.md                  # Ce guide explicatif en français
```

---

## 🚀 Comment Lancer l'Application sur Windows (Guide Pas-à-Pas)

Vous n'avez pas besoin de savoir programmer ! Deux méthodes très simples s'offrent à vous :

### Méthode 1 : La plus simple (En 1 seul double-clic) ⚡
1. Ouvrez votre dossier **`SmartCashAI`** dans l'explorateur de fichiers Windows.
2. Double-cliquez sur le fichier **`lancer_app.bat`**.
3. Une fenêtre noire va s'ouvrir, vérifier vos composants, installer automatiquement les bibliothèques si besoin, puis **ouvrir l'application directement dans votre navigateur web (Google Chrome, Edge, etc.)**.

---

### Méthode 2 : Via le Terminal PowerShell / Invite de Commandes 💻
Si vous préférez lancer l'application manuellement :

1. Ouvrez l'application **PowerShell** ou **Invite de commandes (cmd)** sur Windows.
2. Déplacez-vous dans le dossier du projet :
   ```powershell
   cd C:\Users\Hp\Desktop\SmartCashAI
   ```
3. Installez les bibliothèques nécessaires :
   ```powershell
   pip install -r requirements.txt
   ```
4. Démarrez l'application :
   ```powershell
   streamlit run app.py
   ```
5. Votre navigateur ouvrira automatiquement l'adresse locale : `http://localhost:8501`.

---

## 💡 Scénarios de Démonstration à Tester Immédiatement

Dans la barre latérale gauche de l'application, testez les boutons de démonstration :
- **🟢 Confort** : Observez une trésorerie excédentaire saine avec des conseils de placement.
- **🟠 Tendu** : Observez une trésorerie fragile avec des conseils de relance client.
- **🔴 Critique** : Observez un déficit de trésorerie avec le plan d'action d'urgence bancaire.
- **🤖 Prévision IA** : Pré-remplit automatiquement le formulaire avec les valeurs prédictives calculées par le Machine Learning pour le mois à venir !

---

## 🎓 Note Pédagogique pour les Étudiants
Ce projet illustre parfaitement l'importance de la gestion prévisionnelle de la trésorerie : **une entreprise ne meurt pas nécessairement parce qu'elle n'est pas rentable, mais parce qu'elle n'a plus de liquidités pour payer ses dettes à leur échéance (cessation de paiements)**.
