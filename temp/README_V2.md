# Global Insight Tracker v2.0

## 🚀 Nuovo Sistema Intelligente

Sistema completamente ridisegnato con:
- **Navigazione a grafo** - Ogni sito è un grafo navigabile
- **Auto-discovery** - Trova automaticamente dove sono i report
- **Pipeline per Topic** - Aggrega insights per tema, non per fonte
- **Dashboard moderna** - Per ogni topic: report per company + pensiero aggregato

## 📁 Nuova Architettura

```
Global-Insight-Tracker/
├── tracker.py              # 🎯 Entry point v2.0
├── run_v2.bat              # Script Windows
│
├── site_graph.py           # 🕸️ Rappresentazione siti come grafi
├── route_discovery.py      # 🔍 Auto-discovery delle rotte
├── source_registry.py      # 📋 Censimento fonti con metadata
├── topic_pipeline.py       # ⚙️ Pipeline nodo→tema auto-aggiornante
├── dashboard_generator.py  # 🎨 Genera dashboard per topic
│
├── document_manager.py     # 📥 Download e gestione documenti
├── document_parser.py      # 📄 Parsing PDF/DOCX
├── ai_analyzer.py          # 🤖 Analisi AI (OpenAI/Anthropic)
├── story_builder.py        # 📖 Storytelling aggregato
├── report_generator.py     # 📊 Report HTML/Excel
│
├── data/                   # Dati persistenti
│   ├── sources.json        # Registry fonti
│   ├── graphs/             # Grafi dei siti
│   ├── documents/          # PDF scaricati
│   └── topics_data.json    # Dati aggregati per topic
│
└── output/                 # Output generati
    ├── index.html          # Dashboard latest
    └── dashboard_*.html    # Dashboard storiche
```

## 🏃 Quick Start

### 1. Installa dipendenze
```bash
pip install -r requirements_new.txt
```

### 2. Visualizza fonti disponibili
```bash
python tracker.py sources
```

### 3. Scopri struttura siti
```bash
python tracker.py discover
# O per una fonte specifica:
python tracker.py discover --source deloitte
```

### 4. Scarica report
```bash
python tracker.py fetch
# O per un topic specifico:
python tracker.py fetch --topic AI
```

### 5. Analizza con AI (opzionale)
```bash
# Con OpenAI
export OPENAI_API_KEY=your_key
python tracker.py analyze --ai-provider openai

# Con Anthropic
export ANTHROPIC_API_KEY=your_key
python tracker.py analyze --ai-provider anthropic
```

### 6. Genera dashboard
```bash
python tracker.py dashboard
# Apri output/index.html nel browser
```

### 7. Pipeline completa
```bash
python tracker.py full --ai-provider openai
```

## 🏢 Fonti Preconfigurate

### Consulting (Big 4 + MBB)
- **Deloitte** - Tech Trends, Digital Transformation
- **PwC** - CEO Survey, Digital Trust
- **KPMG** - Global insights
- **EY** - Sustainability focus
- **McKinsey** - MGI research
- **BCG** - Henderson Institute
- **Bain** - Strategy insights
- **Accenture** - Technology Vision

### Research
- **Gartner** - Hype Cycle, Magic Quadrant
- **Forrester** - Technology research

### Think Tanks
- **World Economic Forum** - Global issues
- **Brookings** - Policy research

### Tech Companies
- **Google AI** - Research papers
- **Microsoft Research** - Publications
- **AWS** - Whitepapers

## 📊 Topics Supportati

| Topic | Primary Sources |
|-------|-----------------|
| AI | McKinsey, Deloitte, Google AI |
| Cloud | AWS, Accenture, Gartner |
| Cybersecurity | Deloitte, PwC, Gartner |
| ESG | PwC, EY, WEF |
| Digital Transformation | All consulting |
| Quantum | Google AI, IBM |
| Blockchain | Deloitte, WEF |
| Metaverse | Accenture, Meta |

## 🎨 Dashboard Features

La dashboard mostra per ogni topic:

1. **Executive Summary** - Narrative AI generata
2. **Reports by Company** - Ultimi report organizzati per fonte
3. **Key Insights** - Insights aggregati da tutte le fonti
4. **Navigation** - Navigazione rapida tra topics

## ⚙️ Configurazione

### Variabili Ambiente
```bash
# Per analisi AI
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Aggiungere Nuove Fonti
```python
from source_registry import SourceRegistry, SourceConfig, SourceType

registry = SourceRegistry()
registry.add_source(SourceConfig(
    name="New Source",
    slug="new_source",
    source_type=SourceType.CONSULTING,
    base_url="https://example.com",
    entry_points=["https://example.com/insights"],
    topics=["AI", "Cloud"],
    primary_topics=["AI"]
))
```

## 📅 Auto-Update

La pipeline può essere schedulata:
```python
from topic_pipeline import TopicPipeline

pipeline = TopicPipeline()
pipeline.start_scheduler(interval_hours=24)  # Aggiorna ogni 24 ore
```

## 🔧 Troubleshooting

### Nessun report trovato
- Controlla che i siti non siano bloccati (alcuni richiedono JavaScript)
- Prova `python tracker.py discover --source <source>` per debug

### Errori AI
- Verifica che le API key siano corrette
- Senza AI, usa keyword extraction (meno accurato ma funziona)

### Dashboard vuota
- Assicurati di aver eseguito `fetch` e `analyze` prima
