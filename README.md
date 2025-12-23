# Global Insight Tracker

Monitor automatizzato per white papers e insights su tecnologie dirompenti dalle principali società di consulenza.

## 🚀 Quick Start

```bash
# Installa dipendenze
pip install -r requirements.txt

# Scrape fonti default (Deloitte, McKinsey, BCG)
python run.py scrape

# Scrape specifiche fonti
python run.py scrape --sources deloitte pwc --max 10

# Scrape tutte le fonti + genera dashboard
python run.py scrape --all --dashboard

# Genera dashboard da dati esistenti
python run.py dashboard

# Visualizza statistiche
python run.py stats
```

## 📁 Struttura Progetto

```
Global-Insight-Tracker/
├── run.py                 # Entry point CLI principale
├── requirements.txt       # Dipendenze Python
├── src/                   # Codice sorgente
│   ├── core/             # Moduli core
│   │   ├── config.py     # Configurazione centralizzata
│   │   └── utils.py      # Utility condivise
│   ├── scrapers/         # Scraper per ogni fonte
│   │   ├── base_scraper.py
│   │   ├── selenium_scraper.py
│   │   ├── deloitte.py
│   │   ├── mckinsey.py
│   │   └── bcg.py
│   ├── analyzers/        # Analisi contenuti
│   │   ├── ai_analyzer.py
│   │   └── topic_classifier.py
│   └── generators/       # Generazione output
│       ├── excel_generator.py
│       ├── dashboard_generator.py
│       └── story_builder.py
├── tests/                # Test automatizzati
├── output/               # File generati (Excel, HTML)
├── logs/                 # Log applicazione
├── temp/                 # File temporanei
└── docs/                 # Documentazione
```

## 🎯 Fonti Supportate

| Fonte | Status | Note |
|-------|--------|------|
| Deloitte | ✅ | Deloitte Insights US |
| McKinsey | ✅ | Featured Insights |
| BCG | ✅ | Publications |
| PwC | ✅ | Issues & Insights |
| EY | ✅ | Insights |
| KPMG | ✅ | Our Insights |
| Accenture | ✅ | Technology Index |
| Bain | ✅ | Insights |
| Gartner | ✅ | Insights |
| Forrester | ✅ | Research |

## 📊 Output

- **Excel**: `output/report_consulting.xlsx` - Tutti gli articoli estratti
- **Dashboard**: `output/dashboard.html` - Dashboard interattiva HTML
- **Logs**: `logs/scraping.log` - Log dettagliato

## ⚙️ Configurazione

Modifica `src/core/config.py` per:

- Aggiungere/rimuovere fonti
- Modificare URL e pattern
- Configurare timeout e delay
- Abilitare AI analysis (OpenAI/Anthropic)

### Variabili Ambiente (opzionali)

```bash
# Per AI analysis
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
```

## 🔧 Requisiti

- Python 3.10+
- Chrome/Chromium (per Selenium)
- Connessione internet

## 📝 Comandi

| Comando | Descrizione |
|---------|-------------|
| `python run.py scrape` | Scrape fonti default |
| `python run.py scrape --all` | Scrape tutte le fonti |
| `python run.py scrape -s deloitte bcg` | Scrape fonti specifiche |
| `python run.py scrape --max 20` | Max 20 articoli per fonte |
| `python run.py scrape --dashboard` | Genera anche dashboard |
| `python run.py dashboard` | Genera dashboard da dati |
| `python run.py stats` | Mostra statistiche |

## 🧪 Test

```bash
pytest tests/ -v
```

## 📄 License

MIT
