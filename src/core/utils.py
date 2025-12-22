# -*- coding: utf-8 -*-
"""
Global Insight Tracker - Utilities
==================================

Funzioni di utilità condivise tra i moduli.
"""

import logging
import re
import random
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .config import SCRAPING, LOGS_DIR

# ==============================================================================
# LOGGING SETUP
# ==============================================================================

def setup_logger(name: str = 'insight_tracker', level: int = logging.INFO) -> logging.Logger:
    """
    Configura e ritorna un logger
    
    Args:
        name: Nome del logger
        level: Livello di logging
        
    Returns:
        Logger configurato
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Console handler
    console = logging.StreamHandler()
    console.setLevel(level)
    console_fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                     datefmt='%H:%M:%S')
    console.setFormatter(console_fmt)
    logger.addHandler(console)
    
    # File handler
    log_file = LOGS_DIR / 'scraping.log'
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)
    
    return logger


# Logger globale
logger = setup_logger()

# ==============================================================================
# TEXT UTILITIES  
# ==============================================================================

def clean_text(text: str, max_length: int = 500) -> str:
    """
    Pulisce e normalizza testo
    
    Args:
        text: Testo da pulire
        max_length: Lunghezza massima
        
    Returns:
        Testo pulito
    """
    if not text:
        return ''
    
    # Rimuovi whitespace multipli
    text = re.sub(r'\s+', ' ', text)
    
    # Strip
    text = text.strip()
    
    # Tronca se necessario
    if len(text) > max_length:
        text = text[:max_length-3] + '...'
    
    return text


def extract_text(element: Any) -> str:
    """Estrae testo da elemento BeautifulSoup"""
    if element is None:
        return ''
    
    if isinstance(element, str):
        return clean_text(element)
    
    return clean_text(element.get_text(strip=True))


def slugify(text: str) -> str:
    """Converte testo in slug URL-safe"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

# ==============================================================================
# URL UTILITIES
# ==============================================================================

def normalize_url(url: str, base_url: str = '') -> str:
    """
    Normalizza URL (gestisce relativi/assoluti)
    
    Args:
        url: URL da normalizzare
        base_url: URL base per link relativi
        
    Returns:
        URL completo normalizzato
    """
    if not url:
        return ''
    
    url = url.strip()
    
    # Già assoluto
    if url.startswith('http://') or url.startswith('https://'):
        return url
    
    # Relativo
    if base_url:
        return urljoin(base_url, url)
    
    return url


def extract_domain(url: str) -> str:
    """Estrae dominio da URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return ''


def get_source_name(url: str) -> str:
    """Identifica nome fonte da URL"""
    domain = extract_domain(url)
    
    source_map = {
        'deloitte': 'Deloitte',
        'pwc': 'PwC',
        'mckinsey': 'McKinsey',
        'bcg': 'BCG',
        'ey.com': 'EY',
        'kpmg': 'KPMG',
        'accenture': 'Accenture',
        'bain': 'Bain',
        'gartner': 'Gartner',
        'forrester': 'Forrester',
        'idc': 'IDC',
    }
    
    for pattern, name in source_map.items():
        if pattern in domain:
            return name
    
    # Fallback: capitalizza prima parte dominio
    parts = domain.split('.')
    return parts[0].capitalize() if parts else domain

# ==============================================================================
# HTTP UTILITIES
# ==============================================================================

def get_random_user_agent() -> str:
    """Ritorna User-Agent casuale"""
    return random.choice(SCRAPING.user_agents)


def get_request_headers() -> Dict[str, str]:
    """Ritorna headers HTTP con User-Agent casuale"""
    headers = SCRAPING.headers.copy()
    headers['User-Agent'] = get_random_user_agent()
    return headers

# ==============================================================================
# DATE UTILITIES
# ==============================================================================

def parse_date(date_str: str, formats: List[str] = None) -> Optional[datetime]:
    """
    Parsa stringa data in datetime
    
    Args:
        date_str: Stringa data
        formats: Lista formati da provare
        
    Returns:
        datetime o None
    """
    if not date_str:
        return None
    
    date_str = date_str.strip()
    
    if formats is None:
        formats = [
            '%B %d, %Y',      # December 23, 2025
            '%d %B %Y',       # 23 December 2025
            '%Y-%m-%d',       # 2025-12-23
            '%d/%m/%Y',       # 23/12/2025
            '%m/%d/%Y',       # 12/23/2025
            '%b %d, %Y',      # Dec 23, 2025
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def format_date(dt: Optional[datetime], fmt: str = '%d/%m/%Y') -> str:
    """Formatta datetime in stringa"""
    if dt is None:
        return ''
    return dt.strftime(fmt)

# ==============================================================================
# ARTICLE UTILITIES
# ==============================================================================

def create_article(
    title: str,
    url: str,
    source: str,
    category: str = '',
    description: str = '',
    date: str = '',
    **kwargs
) -> Dict[str, str]:
    """
    Crea dizionario articolo standardizzato
    
    Args:
        title: Titolo articolo
        url: URL articolo
        source: Fonte (es. 'Deloitte')
        category: Categoria/topic
        description: Descrizione/sommario
        date: Data pubblicazione
        **kwargs: Campi aggiuntivi
        
    Returns:
        Dizionario articolo
    """
    return {
        'title': clean_text(title, 200),
        'url': url,
        'source': source,
        'category': category or 'General',
        'description': clean_text(description, 500) or title,
        'date': date,
        'scraped_at': datetime.now().isoformat(),
        **kwargs
    }


def is_relevant(title: str, description: str = '', keywords: List[str] = None) -> bool:
    """
    Verifica se articolo è rilevante per tecnologie dirompenti
    
    Args:
        title: Titolo
        description: Descrizione
        keywords: Lista keyword da cercare
        
    Returns:
        True se rilevante
    """
    from .config import RELEVANCE_KEYWORDS
    
    if keywords is None:
        keywords = RELEVANCE_KEYWORDS
    
    text = f"{title} {description}".lower()
    
    return any(kw in text for kw in keywords)


def deduplicate_articles(articles: List[Dict]) -> List[Dict]:
    """
    Rimuove articoli duplicati per URL
    
    Args:
        articles: Lista articoli
        
    Returns:
        Lista senza duplicati
    """
    seen = set()
    unique = []
    
    for article in articles:
        url = article.get('url', '')
        if url and url not in seen:
            seen.add(url)
            unique.append(article)
    
    return unique

# ==============================================================================
# CATEGORY EXTRACTION
# ==============================================================================

def extract_category_from_url(url: str) -> str:
    """Estrae categoria dal path URL"""
    patterns = {
        'technology': 'Technology',
        'digital': 'Digital Transformation',
        'ai': 'Artificial Intelligence',
        'artificial-intelligence': 'Artificial Intelligence',
        'data': 'Data & Analytics',
        'analytics': 'Data & Analytics',
        'cloud': 'Cloud Computing',
        'cyber': 'Cybersecurity',
        'security': 'Cybersecurity',
        'financial': 'Financial Services',
        'healthcare': 'Healthcare',
        'consumer': 'Consumer',
        'energy': 'Energy',
        'sustainability': 'Sustainability',
        'manufacturing': 'Manufacturing',
    }
    
    url_lower = url.lower()
    
    for pattern, category in patterns.items():
        if pattern in url_lower:
            return category
    
    return 'General'
