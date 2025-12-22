@echo off
REM Global Insight Tracker - Script di Avvio Rapido
REM Questo script configura l'ambiente e avvia lo scraping

echo.
echo ====================================================================
echo  Global Insight Tracker - Sistema di Monitoring White Papers
echo ====================================================================
echo.

REM Controlla se Python è installato
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] Python non trovato! Installare Python 3.8+ da https://www.python.org
    pause
    exit /b 1
)

echo [OK] Python trovato
echo.

REM Controlla se venv esiste
if not exist "venv\" (
    echo [INFO] Creazione virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERRORE] Impossibile creare virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment creato
    echo.
)

REM Attiva venv
echo [INFO] Attivazione virtual environment...
call venv\Scripts\activate.bat

REM Installa/aggiorna dipendenze
echo [INFO] Installazione dipendenze...
pip install --upgrade pip -q
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERRORE] Installazione dipendenze fallita
    pause
    exit /b 1
)
echo [OK] Dipendenze installate
echo.

REM Esegui scraping
echo ====================================================================
echo  AVVIO SCRAPING
echo ====================================================================
echo.

python main.py %*

REM Verifica risultato
if errorlevel 1 (
    echo.
    echo [ERRORE] Scraping terminato con errori
    pause
    exit /b 1
) else (
    echo.
    echo [SUCCESSO] Scraping completato!
    echo.
    echo Il report Excel e' disponibile in: output\report_consulting.xlsx
    echo I log sono disponibili in: logs\scraping.log
    echo.
)

pause
