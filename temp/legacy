# -*- coding: utf-8 -*-
"""
Configurazione URL e Selettori CSS per Web Scraping
Global Insight Tracker - Disruptive Tech Monitor

Questo file contiene tutti i target URL e i selettori CSS/XPath
per estrarre contenuti dai siti delle società di consulenza.

IMPORTANTE: I selettori possono diventare obsoleti se i siti cambiano struttura.
Verificare periodicamente e aggiornare se necessario.
"""

import os

# ==============================================================================
# CONFIGURAZIONE GENERALE
# ==============================================================================

# Directory di base del progetto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory per i report Excel
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

# Directory per i log
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# Nome del file Excel di output
OUTPUT_FILENAME = 'report_consulting.xlsx'

# Numero massimo di articoli da estrarre per sito
MAX_ARTICLES_PER_SITE = 5

# Timeout per le richieste HTTP (secondi)
REQUEST_TIMEOUT = 30

# Delay tra richieste allo stesso dominio (secondi)
REQUEST_DELAY = 3

# Numero di tentativi in caso di errore
MAX_RETRIES = 3

# User-Agent per le richieste HTTP
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

# Headers HTTP standard
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# ==============================================================================
# CONFIGURAZIONE SITI TARGET
# ==============================================================================

SITES_CONFIG = {
    # --------------------------------------------------------------------------
    # DELOITTE - Aggiornato 23/12/2025 con selettori reali
    # --------------------------------------------------------------------------
    'deloitte': {
        'name': 'Deloitte',
        'base_url': 'https://www2.deloitte.com',
        'insights_url': 'https://www2.deloitte.com/us/en/insights.html',
        'alternative_urls': [
            'https://www2.deloitte.com/us/en/insights/focus/tech-trends.html',
            'https://www2.deloitte.com/us/en/insights/topics/digital-transformation.html',
            'https://www2.deloitte.com/us/en/insights/industry/technology.html'
        ],
        'selectors': {
            # Pattern link-based - estrai tutti link /insights/ poi deduplicating
            'article_container': 'a[href*="/insights/"]',
            'title': 'span, h2, h3, h4',  # Cerca testo dentro il link
            'link': '',  # L'elemento stesso è il link
            'date': 'time, span.date',
            'category': 'span.category, span.topic',
            'description': 'p, span.description'
        },
        'extraction_mode': 'link_based',  # Nuovo: estrai da link invece che da container
        'date_format': '%B %d, %Y',
        'requires_selenium': True  # Richiede JS rendering
    },

    # --------------------------------------------------------------------------
    # PWC
    # --------------------------------------------------------------------------
    'pwc': {
        'name': 'PwC',
        'base_url': 'https://www.pwc.com',
        'insights_url': 'https://www.pwc.com/gx/en/issues.html',
        'alternative_urls': [
            'https://www.pwc.com/gx/en/services/consulting.html',
            'https://www.pwc.com/gx/en/issues/data-and-analytics.html',
            'https://www.pwc.com/gx/en/issues/artificial-intelligence.html'
        ],
        'selectors': {
            'article_container': 'div.article-card, div.insight-item, article.publication',
            'title': 'h3.card-title, h2.article-title, a.title-link',
            'link': 'a.article-link, a.card-link',
            'date': 'time, span.date, p.publish-date',
            'category': 'span.category, a.topic',
            'description': 'p.description, div.summary, p.excerpt'
        },
        'date_format': '%d %b %Y',  # es. "15 Dec 2025"
        'requires_selenium': False
    },

    # --------------------------------------------------------------------------
    # EY (Ernst & Young)
    # --------------------------------------------------------------------------
    'ey': {
        'name': 'EY',
        'base_url': 'https://www.ey.com',
        'insights_url': 'https://www.ey.com/en_gl/insights',
        'alternative_urls': [
            'https://www.ey.com/en_gl/insights/technology',
            'https://www.ey.com/en_gl/insights/digital',
            'https://www.ey.com/en_gl/insights/consulting'
        ],
        'selectors': {
            'article_container': 'div.insight-card, article.article-item, div.content-card',
            'title': 'h3.insight-title, h2.card-title, a.article-link',
            'link': 'a.insight-link, a.card-link',
            'date': 'time, span.date, div.article-date',
            'category': 'span.topic, a.category-link',
            'description': 'p.insight-description, div.article-summary, p.teaser'
        },
        'date_format': '%d %B %Y',  # es. "15 December 2025"
        'requires_selenium': False
    },

    # --------------------------------------------------------------------------
    # KPMG
    # --------------------------------------------------------------------------
    'kpmg': {
        'name': 'KPMG',
        'base_url': 'https://kpmg.com',
        'insights_url': 'https://kpmg.com/xx/en/home/insights.html',
        'alternative_urls': [
            'https://kpmg.com/xx/en/home/insights/2024.html',
            'https://kpmg.com/xx/en/home/insights/2025.html'
        ],
        'selectors': {
            'article_container': 'div.insight-item, article.content-card, div.article-wrapper',
            'title': 'h3.title, h2.insight-title, a.article-title',
            'link': 'a.insight-link, a.content-link',
            'date': 'time, span.date, div.publish-date',
            'category': 'span.topic, a.tag',
            'description': 'p.description, div.summary, p.abstract'
        },
        'date_format': '%d/%m/%Y',  # es. "15/12/2025"
        'requires_selenium': False
    },

    # --------------------------------------------------------------------------
    # MCKINSEY & COMPANY
    # --------------------------------------------------------------------------
    'mckinsey': {
        'name': 'McKinsey',
        'base_url': 'https://www.mckinsey.com',
        'insights_url': 'https://www.mckinsey.com/featured-insights',
        'alternative_urls': [
            'https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights',
            'https://www.mckinsey.com/capabilities/quantumblack/our-insights',
            'https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights'
        ],
        'selectors': {
            'article_container': 'article.editorial-card, div.insight-card, div.article-item',
            'title': 'h3.editorial-card__title, h2.insight-title, a.title',
            'link': 'a.editorial-card__link, a.insight-link',
            'date': 'time, span.date, p.publish-date',
            'category': 'span.topic, a.category',
            'description': 'p.editorial-card__description, div.summary, p.excerpt'
        },
        'date_format': '%B %Y',  # es. "December 2025" (spesso solo mese/anno)
        'requires_selenium': True  # McKinsey usa AJAX
    },

    # --------------------------------------------------------------------------
    # BCG (Boston Consulting Group)
    # --------------------------------------------------------------------------
    'bcg': {
        'name': 'BCG',
        'base_url': 'https://www.bcg.com',
        'insights_url': 'https://www.bcg.com/publications',
        'alternative_urls': [
            'https://www.bcg.com/beyond-consulting/bcg-topics/technology-digital',
            'https://www.bcg.com/beyond-consulting/bcg-topics/artificial-intelligence',
            'https://www.bcg.com/beyond-consulting/bcg-topics/digital-transformation'
        ],
        'selectors': {
            'article_container': 'div.publication-card, article.content-item, div.insight-wrapper',
            'title': 'h3.card-title, h2.publication-title, a.title-link',
            'link': 'a.publication-link, a.card-link',
            'date': 'time, span.date, div.publish-date',
            'category': 'span.topic, a.tag',
            'description': 'p.description, div.summary, p.abstract'
        },
        'date_format': '%b %d, %Y',  # es. "Dec 15, 2025"
        'requires_selenium': True  # BCG carica articoli dinamicamente
    }
}

# ==============================================================================
# KEYWORDS PER FILTRO TEMATICHE
# ==============================================================================
# Usate per identificare articoli rilevanti su tecnologie dirompenti

DISRUPTIVE_TECH_KEYWORDS = [
    # AI & Machine Learning
    'artificial intelligence', 'ai', 'machine learning', 'deep learning',
    'generative ai', 'genai', 'gpt', 'llm', 'large language model',
    'neural network', 'computer vision', 'natural language processing', 'nlp',
    
    # Automation & Robotics
    'automation', 'robotic process automation', 'rpa', 'robotics',
    'autonomous', 'intelligent automation',
    
    # Blockchain & Crypto
    'blockchain', 'cryptocurrency', 'bitcoin', 'ethereum', 'defi',
    'decentralized finance', 'web3', 'nft', 'smart contract',
    
    # Cloud & Infrastructure
    'cloud computing', 'edge computing', 'quantum computing',
    'hybrid cloud', 'multicloud', 'serverless',
    
    # Data & Analytics
    'big data', 'data analytics', 'predictive analytics',
    'data science', 'business intelligence',
    
    # Digital Transformation
    'digital transformation', 'digitalization', 'industry 4.0',
    'digital twin', 'iot', 'internet of things',
    
    # Fintech
    'fintech', 'digital banking', 'open banking', 'embedded finance',
    'payment innovation', 'regtech',
    
    # Sustainability & ESG
    'sustainability', 'esg', 'green technology', 'climate tech',
    'carbon neutral', 'renewable energy', 'circular economy',
    
    # Cybersecurity
    'cybersecurity', 'zero trust', 'data privacy', 'gdpr',
    'threat intelligence', 'security',
    
    # Future of Work
    'future of work', 'remote work', 'hybrid work', 'gig economy',
    'workforce transformation', 'upskilling', 'reskilling',
    
    # Healthcare Tech
    'digital health', 'telemedicine', 'healthtech', 'medical ai',
    'precision medicine', 'genomics',
    
    # Emerging Tech
    '5g', '6g', 'metaverse', 'augmented reality', 'virtual reality',
    'ar', 'vr', 'extended reality', 'xr'
]

# ==============================================================================
# CONFIGURAZIONE SELENIUM (per siti dinamici)
# ==============================================================================

SELENIUM_CONFIG = {
    'headless': True,  # Esegui browser invisibile
    'window_size': (1920, 1080),
    'page_load_timeout': 30,
    'implicit_wait': 10,
    'chrome_options': [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-blink-features=AutomationControlled',
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    ]
}

# ==============================================================================
# FORMATO DATE
# ==============================================================================

# Formati di data comuni da parsare
DATE_FORMATS = [
    '%B %d, %Y',      # December 15, 2025
    '%d %B %Y',       # 15 December 2025
    '%b %d, %Y',      # Dec 15, 2025
    '%d %b %Y',       # 15 Dec 2025
    '%Y-%m-%d',       # 2025-12-15
    '%d/%m/%Y',       # 15/12/2025
    '%m/%d/%Y',       # 12/15/2025
    '%B %Y',          # December 2025
    '%b %Y',          # Dec 2025
    '%Y',             # 2025
]

# Formato di output per Excel
EXCEL_DATE_FORMAT = '%d/%m/%Y'

# ==============================================================================
# CONFIGURAZIONE EXCEL
# ==============================================================================

EXCEL_COLUMNS = [
    'Giorno di scrittura',
    'Giorno articolo',
    'Fonte e società',
    'Argomento',
    'Titolo paper',
    'Descrizione'
]

# Larghezza colonne Excel (in caratteri)
EXCEL_COLUMN_WIDTHS = {
    'Giorno di scrittura': 15,
    'Giorno articolo': 15,
    'Fonte e società': 40,
    'Argomento': 20,
    'Titolo paper': 60,
    'Descrizione': 80
}

# ==============================================================================
# CONFIGURAZIONE LOGGING
# ==============================================================================

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FILENAME = 'scraping.log'

# Livelli di log: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = 'INFO'

# ==============================================================================
# FUNZIONI DI UTILITÀ
# ==============================================================================

def get_all_target_urls():
    """Ritorna tutti gli URL da scrapare (principale + alternativi)"""
    urls = []
    for site_key, site_config in SITES_CONFIG.items():
        urls.append({
            'site': site_key,
            'name': site_config['name'],
            'url': site_config['insights_url'],
            'is_alternative': False
        })
        for alt_url in site_config.get('alternative_urls', []):
            urls.append({
                'site': site_key,
                'name': site_config['name'],
                'url': alt_url,
                'is_alternative': True
            })
    return urls

def get_site_config(site_key):
    """Ritorna la configurazione per una specifica società"""
    return SITES_CONFIG.get(site_key)

def is_disruptive_tech_related(text):
    """
    Verifica se un testo contiene keywords relative a tecnologie dirompenti
    
    Args:
        text (str): Testo da analizzare (titolo o descrizione)
    
    Returns:
        bool: True se il testo è rilevante
    """
    if not text:
        return False
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in DISRUPTIVE_TECH_KEYWORDS)

# ==============================================================================
# VALIDAZIONE CONFIGURAZIONE
# ==============================================================================

def validate_config():
    """Valida la configurazione all'avvio"""
    errors = []
    
    # Controlla che tutte le directory esistano
    for dir_path in [OUTPUT_DIR, LOG_DIR]:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except Exception as e:
                errors.append(f"Impossibile creare directory {dir_path}: {e}")
    
    # Controlla che tutti i siti abbiano i campi obbligatori
    required_fields = ['name', 'base_url', 'insights_url', 'selectors']
    for site_key, site_config in SITES_CONFIG.items():
        for field in required_fields:
            if field not in site_config:
                errors.append(f"Sito {site_key}: campo obbligatorio '{field}' mancante")
    
    if errors:
        print("⚠️  ERRORI DI CONFIGURAZIONE:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True

# Esegui validazione all'import
if __name__ != '__main__':
    validate_config()
