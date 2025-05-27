@echo off
echo Installation des dépendances en cours...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors de l'installation des dépendances. Veuillez vérifier que Python est correctement installé.
    pause
    exit /b
)
echo Démarrage de l'Application Kruskal...
python application_kruskal.py
if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors du lancement de l'application.
    pause
)
pause 