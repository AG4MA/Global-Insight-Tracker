# -*- coding: utf-8 -*-
"""
Global Insight Tracker - Configurazione Centralizzata
=====================================================

Configurazione per scraping, API, paths e siti target.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# ==============================================================================
# PATHS
# ==============================================================================

# Directory base del progetto
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"
TEMP_DIR = PROJECT_ROOT / "temp"
DOCS_DIR = PROJECT_ROOT / "docs"

# Crea directory se non esistono
for dir_path in [OUTPUT_DIR, LOGS_DIR, TEMP_DIR]:
    dir_path.mkdir(exist_ok=True)

# ==============================================================================
# SCRAPING SETTINGS
# ==============================================================================

@dataclass
class ScrapingConfig:
    """Configurazione scraping"""
    max_articles_per_site: int = 10
    request_timeout: int = 30
    request_delay: float = 2.0
    max_retries: int = 3
    selenium_wait_time: int = 8
    scroll_for_lazy_load: bool = True
    
    user_agents: List[str] = field(default_factory=lambda: [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    ])
    
    headers: Dict[str, str] = field(default_factory=lambda: {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
    })


# Istanza globale
SCRAPING = ScrapingConfig()

# ==============================================================================
# SELENIUM SETTINGS
# ==============================================================================

@dataclass  
class SeleniumConfig:
    """Configurazione Selenium/Chrome"""
    headless: bool = True
    page_load_timeout: int = 30
    implicit_wait: int = 10
    
    chrome_options: List[str] = field(default_factory=lambda: [
        '--headless=new',
        '--no-sandbox',
        '--disable-gpu',
        '--disable-dev-shm-usage',
        '--window-size=1920,1080',
    ])


SELENIUM = SeleniumConfig()

# ==============================================================================
# SOURCES CONFIGURATION
# ==============================================================================

@dataclass
class SourceConfig:
    """Configurazione singola fonte"""
    name: str
    base_url: str
    insights_url: str
    link_pattern: str  # Pattern per trovare link articoli (es. '/insights/')
    alternative_urls: List[str] = field(default_factory=list)
    requires_selenium: bool = True  # Default: usa Selenium
    enabled: bool = True
    

# Registro delle fonti
SOURCES: Dict[str, SourceConfig] = {
    'deloitte': SourceConfig(
        name='Deloitte',
        base_url='https://www2.deloitte.com',
        insights_url='https://www2.deloitte.com/us/en/insights.html',
        link_pattern='/insights/',
        alternative_urls=[
            'https://www2.deloitte.com/us/en/insights/focus/tech-trends.html',
            'https://www2.deloitte.com/us/en/insights/topics/digital-transformation.html',
        ],
        requires_selenium=True,
    ),
    
    'mckinsey': SourceConfig(
        name='McKinsey',
        base_url='https://www.mckinsey.com',
        insights_url='https://www.mckinsey.com/featured-insights',
        link_pattern='/featured-insights/',
        alternative_urls=[
            'https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights',
            'https://www.mckinsey.com/mgi/overview',
        ],
        requires_selenium=True,
    ),
    
    'bcg': SourceConfig(
        name='BCG',
        base_url='https://www.bcg.com',
        insights_url='https://www.bcg.com/publications',
        link_pattern='/publications/',
        alternative_urls=[
            'https://www.bcg.com/beyond-consulting/bcg-topics/technology-digital',
        ],
        requires_selenium=True,
    ),
    
    'pwc': SourceConfig(
        name='PwC',
        base_url='https://www.pwc.com',
        insights_url='https://www.pwc.com/gx/en/issues.html',
        link_pattern='/issues/',
        alternative_urls=[
            'https://www.pwc.com/gx/en/services/consulting.html',
        ],
        requires_selenium=True,
    ),
    
    'ey': SourceConfig(
        name='EY',
        base_url='https://www.ey.com',
        insights_url='https://www.ey.com/en_gl/insights',
        link_pattern='/insights/',
        alternative_urls=[],
        requires_selenium=True,
    ),
    
    'kpmg': SourceConfig(
        name='KPMG',
        base_url='https://kpmg.com',
        insights_url='https://kpmg.com/xx/en/our-insights.html',
        link_pattern='/insights/',
        alternative_urls=[],
        requires_selenium=True,
    ),
    
    'accenture': SourceConfig(
        name='Accenture',
        base_url='https://www.accenture.com',
        insights_url='https://www.accenture.com/us-en/insights/technology-index',
        link_pattern='/insights/',
        alternative_urls=[],
        requires_selenium=True,
    ),
    
    'bain': SourceConfig(
        name='Bain',
        base_url='https://www.bain.com',
        insights_url='https://www.bain.com/insights/',
        link_pattern='/insights/',
        alternative_urls=[],
        requires_selenium=True,
    ),
    
    'gartner': SourceConfig(
        name='Gartner',
        base_url='https://www.gartner.com',
        insights_url='https://www.gartner.com/en/insights',
        link_pattern='/insights/',
        alternative_urls=[],
        requires_selenium=True,
    ),
    
    'forrester': SourceConfig(
        name='Forrester',
        base_url='https://www.forrester.com',
        insights_url='https://www.forrester.com/research/',
        link_pattern='/research/',
        alternative_urls=[],
        requires_selenium=True,
    ),
}


def get_source(name: str) -> Optional[SourceConfig]:
    """Ottieni configurazione fonte per nome"""
    return SOURCES.get(name.lower())


def get_enabled_sources() -> Dict[str, SourceConfig]:
    """Ottieni tutte le fonti abilitate"""
    return {k: v for k, v in SOURCES.items() if v.enabled}


# ==============================================================================
# AI SETTINGS (Optional)
# ==============================================================================

@dataclass
class AIConfig:
    """Configurazione AI analysis"""
    openai_api_key: str = os.getenv('OPENAI_API_KEY', '')
    anthropic_api_key: str = os.getenv('ANTHROPIC_API_KEY', '')
    model: str = 'gpt-4o-mini'
    max_tokens: int = 1000
    enabled: bool = False  # Disabilitato di default


AI = AIConfig()

# ==============================================================================
# OUTPUT SETTINGS
# ==============================================================================

@dataclass
class OutputConfig:
    """Configurazione output"""
    excel_filename: str = 'report_consulting.xlsx'
    dashboard_filename: str = 'dashboard.html'
    json_filename: str = 'insights.json'


OUTPUT = OutputConfig()

# ==============================================================================
# TOPICS / CATEGORIES
# ==============================================================================

TOPICS = [
    'Artificial Intelligence',
    'Machine Learning', 
    'Generative AI',
    'Cloud Computing',
    'Cybersecurity',
    'Digital Transformation',
    'Data Analytics',
    'Blockchain',
    'Internet of Things',
    'Quantum Computing',
    'Sustainability',
    'Future of Work',
]

RELEVANCE_KEYWORDS = [
    'ai', 'artificial intelligence', 'machine learning', 'deep learning',
    'generative ai', 'genai', 'llm', 'large language model', 'gpt', 'chatgpt',
    'cloud', 'aws', 'azure', 'gcp', 'saas', 'paas', 'iaas',
    'cybersecurity', 'security', 'ransomware', 'zero trust',
    'digital transformation', 'digitalization', 'automation',
    'data analytics', 'big data', 'data science', 'business intelligence',
    'blockchain', 'web3', 'crypto', 'defi', 'nft',
    'iot', 'internet of things', 'edge computing', 'smart devices',
    'quantum', 'quantum computing', 'qubits',
    'metaverse', 'ar', 'vr', 'augmented reality', 'virtual reality',
    '5g', '6g', 'telecommunications',
    'sustainability', 'esg', 'green tech', 'climate tech',
]
