@echo off
title SmartCash AI - Lancement de l'application
chcp 65001 > nul
cls

echo ======================================================================
echo       SMARTCASH AI MAROC 🇲🇦 — PRÉVISION INTELLIGENTE DE TRÉSORERIE
echo             Votre trésorerie, anticipée intelligemment (MAD)
echo ======================================================================
echo.
echo Vérification de l'environnement Python...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'a pas été détecté sur votre machine.
    echo Veuillez installer Python 3.10+ et cocher 'Add Python to PATH'.
    pause
    exit /b
)

echo Démarrage du serveur local Streamlit...
echo L'application va s'ouvrir automatiquement dans votre navigateur par défaut.
echo Appuyez sur Ctrl+C dans cette fenêtre pour arrêter l'application.
echo.

python -m streamlit run app.py --server.port 8501

if %errorlevel% neq 0 (
    echo.
    echo [ERREUR] Une erreur s'est produite lors de l'exécution de Streamlit.
    pause
)

