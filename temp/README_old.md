"# 📊 Global Insight Tracker - Disruptive Tech Monitor

## 🎯 Obiettivo del Progetto

**Global Insight Tracker** è uno strumento automatizzato di web scraping per monitorare e aggregare i più recenti white papers, insights e report sulle tecnologie dirompenti pubblicati dalle principali società di consulenza globali.

### Società Monitorate
- **Big 4**: Deloitte, PwC, EY, KPMG
- **Top Strategy Consulting**: McKinsey & Company, Boston Consulting Group (BCG)

### Focus Tematico
Il sistema si concentra su articoli e report riguardanti:
- 🤖 **Intelligenza Artificiale & Automazione** (GenAI, ML, RPA)
- 🌱 **Sostenibilità & ESG** (Green Tech, Climate Change)
- 💰 **Fintech & Digital Banking** (Blockchain, DeFi, Open Banking)
- 🏥 **Digital Transformation** (Healthcare Tech, Industry 4.0)
- 👔 **Future of Work** (Remote Work, Gig Economy)
- 🔐 **Cybersecurity & Privacy**
- 📊 **Data Analytics & Big Data**

---

## 🏗️ Architettura del Sistema

### Stack Tecnologico
```
Python 3.8+
├── requests            # HTTP client per web scraping
├── BeautifulSoup4      # Parsing HTML
├── Selenium/Playwright # Scraping siti dinamici (se necessario)
├── pandas              # Manipolazione e analisi dati
├── openpyxl            # Gestione file Excel
└── python-dateutil     # Parsing e formattazione date
```

### Struttura del Progetto
```
Big4-Watchdog/
├── README.md                  # Questa documentazione
├── requirements.txt           # Dipendenze Python
├── config.py                  # Configurazione URL e selettori
├── utils.py                   # Funzioni di utilità
├── main.py                    # Script principale
├── scrapers/                  # Moduli scraper specifici per sito
│   ├── __init__.py
│   ├── deloitte_scraper.py
│   ├── pwc_scraper.py
│   ├── ey_scraper.py
│   ├── kpmg_scraper.py
│   ├── mckinsey_scraper.py
│   └── bcg_scraper.py
├── logs/                      # File di log
│   └── scraping.log
└── output/                    # Report Excel generati
    └── report_consulting.xlsx
```

---

## 📋 Formato Output Excel

Il sistema genera un file `report_consulting.xlsx` con le seguenti colonne:

| Colonna | Descrizione | Formato Esempio |
|---------|-------------|-----------------|
| **Giorno di scrittura** | Data di esecuzione dello script | 22/12/2025 |
| **Giorno articolo** | Data di pubblicazione originale | 15/12/2025 o "N/A" |
| **Fonte e società** | Nome società + URL base | Deloitte - https://www2.deloitte.com |
| **Argomento** | Categoria/Tag principale | AI, Sustainability, Fintech |
| **Titolo paper** | Titolo completo del report | "The State of Generative AI 2025" |
| **Descrizione** | Sintesi breve (max 300 caratteri) | "An in-depth analysis of how GenAI..." |

### Caratteristiche Output
- ✅ **Modalità Append**: Nuove righe aggiunte senza cancellare dati esistenti
- ✅ **Deduplicazione**: Controllo per evitare duplicati basato su Titolo + Fonte
- ✅ **Formattazione Automatica**: Date uniformi, testi puliti
- ✅ **Gestione Errori**: Valori mancanti marcati come "N/A"

---

## 🔧 Installazione

### 1. Clona il Repository
```bash
cd c:\projects\Big4-Watchdog
```

### 2. Crea un Virtual Environment (Raccomandato)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Installa le Dipendenze
```bash
pip install -r requirements.txt
```

### 4. (Opzionale) Setup Browser per Selenium
Se alcuni siti richiedono Selenium:
```bash
# Installa ChromeDriver o usa webdriver-manager
pip install webdriver-manager
```

---

## 🚀 Utilizzo

### Esecuzione Standard
```bash
python main.py
```

### Parametri Opzionali
```bash
# Specifica numero di articoli per sito (default: 5)
python main.py --max-articles 10

# Esegui solo per società specifiche
python main.py --companies deloitte pwc

# Output personalizzato
python main.py --output custom_report.xlsx

# Modalità verbose per debug
python main.py --verbose
```

---

## 🔍 Logica di Funzionamento

### Flusso di Esecuzione
1. **Inizializzazione**
   - Carica configurazione URL e selettori CSS
   - Verifica esistenza file Excel (crea o apre in append mode)
   - Inizializza sistema di logging

2. **Scraping Multi-Sito**
   ```
   Per ogni società (Deloitte, PwC, EY, KPMG, McKinsey, BCG):
     ├── Accedi alla pagina "Insights" con User-Agent rotativo
     ├── Attendi caricamento (gestisci AJAX se necessario)
     ├── Estrai ultimi 5 articoli con selettori CSS specifici
     ├── Per ogni articolo:
     │   ├── Estrai: Titolo, URL, Data, Categoria, Descrizione
     │   ├── Pulisci testo (rimuovi HTML, normalizza spazi)
     │   └── Valida dati (controlla campi obbligatori)
     └── Gestisci errori (timeout, cambio struttura HTML)
   ```

3. **Data Processing**
   - Converte date in formato unificato (DD/MM/YYYY)
   - Tronca descrizioni lunghe (max 300 caratteri)
   - Rimuove duplicati confrontando Titolo + Fonte

4. **Export Excel**
   - Carica file esistente (se presente)
   - Aggiungi nuove righe mantenendo storico
   - Formatta colonne (larghezza auto, font)
   - Salva con timestamp nel nome (opzionale)

---

## 🛡️ Gestione Errori

### Strategia di Resilienza
- **Try-Except per Ogni Sito**: Un errore su Deloitte non blocca lo scraping di PwC
- **Retry Logic**: 3 tentativi con backoff esponenziale (1s, 2s, 4s)
- **Timeout HTTP**: 30 secondi per richiesta
- **Logging Dettagliato**: Errori salvati in `logs/scraping.log`
- **Valori di Fallback**: Se un campo manca, inserisci "N/A" invece di crashare

### Tipi di Errori Gestiti
```python
# Errori di rete
requests.exceptions.ConnectionError
requests.exceptions.Timeout

# Errori di parsing
AttributeError  # Selettore CSS non trova elemento
IndexError      # Lista vuota

# Errori di data
ValueError      # Formato data non riconosciuto
```

---

## 📊 Esempi di URL Target

### Deloitte
- Insights: `https://www2.deloitte.com/us/en/insights.html`
- Tech Trends: `https://www2.deloitte.com/us/en/insights/focus/tech-trends.html`

### PwC
- Insights: `https://www.pwc.com/gx/en/issues.html`
- Research: `https://www.pwc.com/gx/en/research-insights.html`

### EY
- Insights: `https://www.ey.com/en_gl/insights`
- Megatrends: `https://www.ey.com/en_gl/megatrends`

### KPMG
- Insights: `https://kpmg.com/xx/en/home/insights.html`

### McKinsey
- Insights: `https://www.mckinsey.com/featured-insights`
- Industries: `https://www.mckinsey.com/industries`

### BCG
- Insights: `https://www.bcg.com/publications`
- Topics: `https://www.bcg.com/beyond-consulting/bcg-topics`

---

## 🔄 Automazione e Scheduling

### Windows Task Scheduler
Esegui lo script ogni lunedì alle 9:00:
```xml
<!-- Crea un task in Windows Task Scheduler -->
Trigger: Weekly, Monday, 09:00
Action: Start a program
Program: C:\projects\Big4-Watchdog\venv\Scripts\python.exe
Arguments: C:\projects\Big4-Watchdog\main.py
```

### Cron Job (Linux/Mac)
```bash
# Aggiungi al crontab
0 9 * * 1 cd /projects/Big4-Watchdog && /usr/bin/python3 main.py
```

### GitHub Actions (CI/CD)
```yaml
# .github/workflows/scrape.yml
name: Weekly Scraping
on:
  schedule:
    - cron: '0 9 * * 1'  # Ogni lunedì 9:00 UTC
jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Scraper
        run: |
          pip install -r requirements.txt
          python main.py
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: report
          path: output/report_consulting.xlsx
```

---

## 🧪 Testing e Validazione

### Test Manuale
```bash
# Test singola società
python -c "from scrapers.deloitte_scraper import scrape_deloitte; print(scrape_deloitte())"

# Verifica formato Excel
python -c "import pandas as pd; print(pd.read_excel('output/report_consulting.xlsx').head())"
```

### Test Automatici (TODO)
```bash
pytest tests/
```

---

## ⚖️ Considerazioni Legali e Etiche

### Best Practices
✅ **Rispetta robots.txt**: Controlla sempre `https://site.com/robots.txt`
✅ **Rate Limiting**: Pausa 2-5 secondi tra le richieste
✅ **User-Agent Realistico**: Identifica il bot correttamente
✅ **Uso Personale/Ricerca**: Non rivendere o redistribuire contenuti

### Termini di Servizio
⚠️ **Disclaimer**: Questo tool è per scopi educativi e di ricerca. L'utente è responsabile di verificare che l'uso sia conforme ai ToS dei siti target.

---

## 🐛 Troubleshooting

### Problema: "Nessun articolo trovato"
**Causa**: Selettori CSS obsoleti (il sito ha cambiato struttura HTML)
**Soluzione**: 
1. Apri la pagina Insights nel browser
2. Ispeziona elemento (F12)
3. Aggiorna i selettori in `config.py`

### Problema: "403 Forbidden" o "429 Too Many Requests"
**Causa**: Il sito blocca il bot
**Soluzione**:
- Aumenta il delay tra richieste (5-10 secondi)
- Usa Selenium con browser headless
- Configura proxy rotanti

### Problema: "Excel file corrupted"
**Causa**: Scrittura interrotta durante l'esecuzione
**Soluzione**:
- Usa backup automatico prima della scrittura
- Implementa lock file per evitare accessi concorrenti

---

## 🚧 Roadmap Future

- [ ] **Database Integration**: SQLite per storico completo
- [ ] **Dashboard Web**: Flask/Streamlit per visualizzazione interattiva
- [ ] **NLP Analysis**: Sentiment analysis e topic modeling sui testi
- [ ] **Email Notifications**: Alert automatici per nuovi report rilevanti
- [ ] **Multi-Language**: Support per insights in lingue diverse dall'inglese
- [ ] **API REST**: Endpoint per integrazione con altri sistemi

---

## 📧 Supporto

Per problemi o suggerimenti:
1. Controlla la sezione [Troubleshooting](#-troubleshooting)
2. Verifica i log in `logs/scraping.log`
3. Apri una issue su GitHub (se applicabile)

---

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi `LICENSE` per dettagli.

---

**Ultimo aggiornamento**: 22 Dicembre 2025  
**Versione**: 1.0.0  
**Autore**: Senior Python Developer Team" 
"# Global-Insight-Tracker" 
"# Global-Insight-Tracker" 
