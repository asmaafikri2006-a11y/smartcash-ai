@echo off
chcp 65001 > nul
title SmartCash AI - Lancement de l'Application

echo ========================================================
echo        🚀 LANCEMENT DE SMARTCASH AI (STREAMLIT)
echo     Outil de Prévision de Trésorerie d'Entreprise
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/3] Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'a pas ete detecte sur votre ordinateur !
    echo Veuillez installer Python depuis https://www.python.org/
    echo Pensez a cocher la case "Add Python to PATH" lors de l'installation.
    pause
    exit /b
)

echo [2/3] Verification et installation des dependances (streamlit, pandas, scikit-learn, plotly)...
python -m pip install -r requirements.txt --quiet

echo [3/3] Demarrage de SmartCash AI dans votre navigateur web...
echo.
echo L'application va s'ouvrir automatiquement dans quelques secondes !
echo Pour arreter l'application, fermez simplement cette fenetre noire.
echo.

python -m streamlit run app.py

pause
