@echo off
echo Installation des dependances en cours...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors de l'installation des dependances. Veuillez verifier que Python est correctement installe.
    pause
    exit /b
)
echo Demarrage de l'Application Kruskal...
python application_kruskal.py
if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors du lancement de l'application.
    pause
)
pause 
