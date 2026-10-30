@echo off
title SmartCash AI - Envoi vers GitHub
echo ============================================================
echo   SmartCash AI - Envoi vers GitHub (Push)
echo   Depot : https://github.com/asmaafikri2006-a11y/smartcash-ai
echo   Compte cible : asmaafikri2006-a11y
echo ============================================================
echo.
echo Envoi en cours... Si une fenetre de connexion GitHub apparait,
echo veuillez vous connecter avec le compte asmaafikri2006-a11y.
echo.
git push -u origin main
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo   [SUCCES] Projet envoye sur GitHub avec succes !
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo   [CONSEIL EN CAS DE REFUS (403)] :
    echo   Si Windows utilise un autre compte GitHub memorise,
    echo   allez dans :
    echo   Panneau de configuration -^> Gestionnaire d'identification
    echo   -^> Informations d'identification Windows -^> Supprimez "git:https://github.com"
    echo   puis relancez ce fichier pour vous connecter avec asmaafikri2006-a11y.
    echo ============================================================
)
echo.
pause
