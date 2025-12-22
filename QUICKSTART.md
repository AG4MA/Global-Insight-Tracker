# 🚀 Quick Start Guide - Global Insight Tracker

## Installazione Rapida (5 minuti)

### 1. Prerequisiti
```bash
# Verifica versione Python (richiesto 3.8+)
python --version
```

### 2. Clona/Naviga al Progetto
```bash
cd c:\projects\Big4-Watchdog
```

### 3. Crea Virtual Environment
```bash
python -m venv venv
```

### 4. Attiva Virtual Environment
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 5. Installa Dipendenze
```bash
pip install -r requirements.txt
```

### 6. Test del Sistema
```bash
python test_system.py
```

### 7. Esegui Primo Scraping
```bash
# Scraping completo (tutte le società)
python main.py

# Scraping solo Deloitte (per test veloce)
python main.py --companies deloitte --max-articles 3
```

---

## 📝 Comandi Utili

### Scraping Base
```bash
# Tutte le società, 5 articoli ciascuna (default)
python main.py

# Output personalizzato
python main.py --output report_gennaio.xlsx

# Modalità verbose (per debug)
python main.py --verbose
```

### Scraping Selettivo
```bash
# Solo Big 4
python main.py --companies deloitte pwc ey kpmg

# Solo società specifiche
python main.py --companies mckinsey bcg

# Più articoli per sito
python main.py --max-articles 10
```

### Comandi Combinati
```bash
# Test rapido con debug
python main.py --companies deloitte --max-articles 2 --verbose

# Report settimanale completo
python main.py --max-articles 10 --output report_week_51.xlsx
```

---

## 🔍 Verifica Risultati

### Dove Trovare l'Output
- **Report Excel**: `output/report_consulting.xlsx`
- **Log dettagliati**: `logs/scraping.log`

### Apri Report Excel
```bash
# Windows
start output\report_consulting.xlsx

# Linux
xdg-open output/report_consulting.xlsx

# Mac
open output/report_consulting.xlsx
```

### Leggi Log
```bash
# Ultimi 50 righe
type logs\scraping.log | more

# Linux/Mac
tail -n 50 logs/scraping.log
```

---

## 🛠️ Troubleshooting Rapido

### Problema: "ModuleNotFoundError"
```bash
# Soluzione: Reinstalla dipendenze
pip install -r requirements.txt --upgrade
```

### Problema: "Nessun articolo trovato"
**Causa**: Selettori CSS obsoleti

**Soluzione**:
1. Apri il sito target nel browser
2. Ispeziona HTML (F12)
3. Aggiorna selettori in `config.py`

### Problema: "403 Forbidden"
**Causa**: Sito blocca il bot

**Soluzione**:
- Aumenta delay in `config.py`: `REQUEST_DELAY = 5`
- Cambia User-Agent in `config.py`

### Problema: Selenium non funziona
```bash
# Installa ChromeDriver automaticamente
pip install webdriver-manager
```

---

## 📊 Formato Output Excel

Il file `report_consulting.xlsx` contiene:

| Colonna | Esempio |
|---------|---------|
| Giorno di scrittura | 22/12/2025 |
| Giorno articolo | 15/12/2025 |
| Fonte e società | Deloitte - https://... |
| Argomento | AI, Fintech |
| Titolo paper | "The Future of..." |
| Descrizione | "An analysis of..." |

---

## 🔄 Automazione

### Windows Task Scheduler

1. Apri Task Scheduler
2. **Action** → **Create Basic Task**
3. **Name**: Global Insight Tracker Weekly
4. **Trigger**: Weekly, Monday, 09:00
5. **Action**: Start a program
   - **Program**: `C:\projects\Big4-Watchdog\venv\Scripts\python.exe`
   - **Arguments**: `C:\projects\Big4-Watchdog\main.py`
   - **Start in**: `C:\projects\Big4-Watchdog`

### Linux Cron

```bash
# Modifica crontab
crontab -e

# Aggiungi (esegui ogni lunedì alle 9:00)
0 9 * * 1 cd /projects/Big4-Watchdog && ./venv/bin/python main.py
```

---

## 💡 Tips & Tricks

### 1. Filtraggio per Topic
Modifica `DISRUPTIVE_TECH_KEYWORDS` in `config.py` per personalizzare le tematiche.

### 2. Export CSV
```python
# Aggiungi in main.py
df.to_csv('output/report.csv', index=False)
```

### 3. Notifiche Email
```python
# Integra SMTP per alert automatici
import smtplib
```

### 4. Database invece di Excel
```python
# Usa SQLite per storico completo
import sqlite3
```

---

## 📚 Documentazione Completa

Per la documentazione completa, vedi [README.md](README.md)

---

## 🆘 Supporto

- **Log**: `logs/scraping.log`
- **Config**: `config.py`
- **Test**: `python test_system.py`

**Ultimo aggiornamento**: 22 Dicembre 2025
