# -*- coding: utf-8 -*-
"""
Funzioni di Utilità - 
Modulo contenente helper functions per web scraping, parsing, e gestione dati
"""

import os
import re
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse

import pandas as pd
from bs4 import BeautifulSoup
import requests
from dateutil import parser as date_parser

import config

# ==============================================================================
# CONFIGURAZIONE LOGGING
# ==============================================================================

def setup_logging():
    """Configura il sistema di logging per l'applicazione"""
    # Crea directory log se non esiste
    if not os.path.exists(config.LOG_DIR):
        os.makedirs(config.LOG_DIR)
    
    log_file = os.path.join(config.LOG_DIR, config.LOG_FILENAME)
    
    # Configura logger
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        datefmt=config.LOG_DATE_FORMAT,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("="*80)
    logger.info("Global Insight Tracker - Sistema di logging inizializzato")
    logger.info("="*80)
    
    return logger

logger = setup_logging()

# ==============================================================================
# FUNZIONI PER RICHIESTE HTTP
# ==============================================================================

def get_random_user_agent() -> str:
    """Ritorna un User-Agent casuale dalla lista configurata"""
    import random
    return random.choice(config.USER_AGENTS)

def make_request(url: str, retries: int = None, timeout: int = None) -> Optional[requests.Response]:
    """
    Esegue una richiesta HTTP con retry logic e gestione errori
    
    Args:
        url: URL da richiedere
        retries: Numero di tentativi (default da config)
        timeout: Timeout in secondi (default da config)
    
    Returns:
        Response object o None in caso di errore
    """
    if retries is None:
        retries = config.MAX_RETRIES
    if timeout is None:
        timeout = config.REQUEST_TIMEOUT
    
    headers = config.HEADERS.copy()
    headers['User-Agent'] = get_random_user_agent()
    
    for attempt in range(retries):
        try:
            logger.info(f"📡 Richiesta a {url} (tentativo {attempt + 1}/{retries})")
            
            response = requests.get(
                url,
                headers=headers,
                timeout=timeout,
                allow_redirects=True
            )
            
            response.raise_for_status()
            
            logger.info(f"✅ Risposta ricevuta: {response.status_code} - {len(response.content)} bytes")
            
            # Delay per essere gentili con il server
            time.sleep(config.REQUEST_DELAY)
            
            return response
        
        except requests.exceptions.Timeout:
            logger.warning(f"⏱️  Timeout per {url} (tentativo {attempt + 1}/{retries})")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Backoff esponenziale
        
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"🔌 Errore di connessione per {url}: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP Error {e.response.status_code} per {url}")
            if e.response.status_code == 403:
                logger.error("   → Possibile blocco anti-bot. Considera di usare Selenium.")
            return None
        
        except Exception as e:
            logger.error(f"❌ Errore imprevisto per {url}: {type(e).__name__} - {e}")
            return None
    
    logger.error(f"❌ Tutti i tentativi falliti per {url}")
    return None

# ==============================================================================
# FUNZIONI PER PARSING HTML
# ==============================================================================

def parse_html(html_content: str) -> Optional[BeautifulSoup]:
    """
    Parsa contenuto HTML con BeautifulSoup
    
    Args:
        html_content: Stringa HTML da parsare
    
    Returns:
        Oggetto BeautifulSoup o None
    """
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        return soup
    except Exception as e:
        logger.error(f"❌ Errore parsing HTML: {e}")
        return None

def extract_text(element, strip: bool = True) -> str:
    """
    Estrae testo da un elemento BeautifulSoup
    
    Args:
        element: Elemento BeautifulSoup o None
        strip: Se True, rimuove spazi bianchi
    
    Returns:
        Testo estratto o stringa vuota
    """
    if element is None:
        return ""
    
    try:
        text = element.get_text(strip=strip)
        return clean_text(text)
    except Exception:
        return ""

def extract_link(element, base_url: str) -> str:
    """
    Estrae URL da un elemento e lo rende assoluto
    
    Args:
        element: Elemento BeautifulSoup con href/src
        base_url: URL base per link relativi
    
    Returns:
        URL assoluto o stringa vuota
    """
    if element is None:
        return ""
    
    try:
        # Cerca href o src
        href = element.get('href') or element.get('src') or ""
        
        if not href:
            return ""
        
        # Converti in URL assoluto
        absolute_url = urljoin(base_url, href)
        return absolute_url
    
    except Exception:
        return ""

def find_element_by_selectors(soup: BeautifulSoup, selectors: str) -> Optional[Any]:
    """
    Cerca un elemento usando multipli selettori CSS (separati da virgola)
    
    Args:
        soup: Oggetto BeautifulSoup
        selectors: Selettori CSS separati da virgola
    
    Returns:
        Primo elemento trovato o None
    """
    if not soup or not selectors:
        return None
    
    for selector in selectors.split(','):
        selector = selector.strip()
        try:
            element = soup.select_one(selector)
            if element:
                return element
        except Exception:
            continue
    
    return None

def find_elements_by_selectors(soup: BeautifulSoup, selectors: str, limit: int = None) -> List[Any]:
    """
    Cerca elementi usando multipli selettori CSS
    
    Args:
        soup: Oggetto BeautifulSoup
        selectors: Selettori CSS separati da virgola
        limit: Numero massimo di elementi da ritornare
    
    Returns:
        Lista di elementi
    """
    if not soup or not selectors:
        return []
    
    for selector in selectors.split(','):
        selector = selector.strip()
        try:
            elements = soup.select(selector, limit=limit)
            if elements:
                return elements
        except Exception:
            continue
    
    return []

# ==============================================================================
# FUNZIONI PER PULIZIA TESTI
# ==============================================================================

def clean_text(text: str) -> str:
    """
    Pulisce una stringa di testo rimuovendo:
    - Spazi multipli
    - Newline multipli
    - Caratteri speciali problematici
    
    Args:
        text: Testo da pulire
    
    Returns:
        Testo pulito
    """
    if not text:
        return ""
    
    # Rimuovi tag HTML residui
    text = re.sub(r'<[^>]+>', '', text)
    
    # Normalizza spazi bianchi
    text = re.sub(r'\s+', ' ', text)
    
    # Rimuovi spazi all'inizio e fine
    text = text.strip()
    
    # Rimuovi caratteri di controllo
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    return text

def truncate_text(text: str, max_length: int = 300, suffix: str = '...') -> str:
    """
    Tronca un testo a una lunghezza massima
    
    Args:
        text: Testo da troncare
        max_length: Lunghezza massima
        suffix: Suffisso da aggiungere se troncato
    
    Returns:
        Testo troncato
    """
    if not text or len(text) <= max_length:
        return text
    
    # Tronca all'ultimo spazio prima di max_length
    truncated = text[:max_length].rsplit(' ', 1)[0]
    return truncated + suffix

def normalize_whitespace(text: str) -> str:
    """Normalizza spazi bianchi in un testo"""
    return ' '.join(text.split())

# ==============================================================================
# FUNZIONI PER PARSING DATE
# ==============================================================================

def parse_date(date_string: str, format_hint: str = None) -> Optional[datetime]:
    """
    Parsa una stringa di data in oggetto datetime
    
    Args:
        date_string: Stringa contenente la data
        format_hint: Formato suggerito (es. '%B %d, %Y')
    
    Returns:
        Oggetto datetime o None
    """
    if not date_string:
        return None
    
    # Pulisci la stringa
    date_string = clean_text(date_string)
    
    # Prova con il formato suggerito
    if format_hint:
        try:
            return datetime.strptime(date_string, format_hint)
        except ValueError:
            pass
    
    # Prova con formati comuni
    for date_format in config.DATE_FORMATS:
        try:
            return datetime.strptime(date_string, date_format)
        except ValueError:
            continue
    
    # Prova con dateutil (parsing intelligente)
    try:
        return date_parser.parse(date_string, fuzzy=True)
    except Exception:
        pass
    
    logger.warning(f"⚠️  Impossibile parsare data: '{date_string}'")
    return None

def format_date(date_obj: datetime, format_str: str = None) -> str:
    """
    Formatta un oggetto datetime in stringa
    
    Args:
        date_obj: Oggetto datetime
        format_str: Formato output (default da config)
    
    Returns:
        Data formattata o "N/A"
    """
    if not date_obj:
        return "N/A"
    
    if format_str is None:
        format_str = config.EXCEL_DATE_FORMAT
    
    try:
        return date_obj.strftime(format_str)
    except Exception:
        return "N/A"

def get_today_formatted() -> str:
    """Ritorna la data odierna formattata per Excel"""
    return format_date(datetime.now())

# ==============================================================================
# FUNZIONI PER GESTIONE EXCEL
# ==============================================================================

def create_excel_file(filepath: str) -> bool:
    """
    Crea un nuovo file Excel con le colonne corrette
    
    Args:
        filepath: Percorso del file da creare
    
    Returns:
        True se successo, False altrimenti
    """
    try:
        # Crea DataFrame vuoto con colonne
        df = pd.DataFrame(columns=config.EXCEL_COLUMNS)
        
        # Crea directory se non esiste
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Salva Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Insights')
            
            # Formatta colonne
            worksheet = writer.sheets['Insights']
            for col_name, width in config.EXCEL_COLUMN_WIDTHS.items():
                col_idx = config.EXCEL_COLUMNS.index(col_name) + 1
                col_letter = chr(64 + col_idx)  # A=65, B=66, etc.
                worksheet.column_dimensions[col_letter].width = width
        
        logger.info(f"✅ File Excel creato: {filepath}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Errore creazione Excel: {e}")
        return False

def load_existing_data(filepath: str) -> pd.DataFrame:
    """
    Carica dati esistenti da file Excel
    
    Args:
        filepath: Percorso del file Excel
    
    Returns:
        DataFrame con dati esistenti o DataFrame vuoto
    """
    if not os.path.exists(filepath):
        logger.info("📄 Nessun file esistente, creazione nuovo Excel")
        return pd.DataFrame(columns=config.EXCEL_COLUMNS)
    
    try:
        df = pd.read_excel(filepath, sheet_name='Insights')
        logger.info(f"📊 Caricati {len(df)} record esistenti da Excel")
        return df
    
    except Exception as e:
        logger.error(f"❌ Errore caricamento Excel: {e}")
        return pd.DataFrame(columns=config.EXCEL_COLUMNS)

def append_to_excel(filepath: str, new_data: List[Dict[str, str]]) -> bool:
    """
    Aggiunge nuovi dati al file Excel esistente (append mode)
    
    Args:
        filepath: Percorso del file Excel
        new_data: Lista di dizionari con i nuovi record
    
    Returns:
        True se successo, False altrimenti
    """
    if not new_data:
        logger.info("ℹ️  Nessun nuovo dato da aggiungere")
        return True
    
    try:
        # Carica dati esistenti
        existing_df = load_existing_data(filepath)
        
        # Crea DataFrame con nuovi dati
        new_df = pd.DataFrame(new_data, columns=config.EXCEL_COLUMNS)
        
        # Rimuovi duplicati (basato su Titolo + Fonte)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        
        # Deduplicazione
        before_count = len(combined_df)
        combined_df = combined_df.drop_duplicates(
            subset=['Titolo paper', 'Fonte e società'],
            keep='first'
        )
        after_count = len(combined_df)
        
        duplicates_removed = before_count - after_count
        if duplicates_removed > 0:
            logger.info(f"🔄 Rimossi {duplicates_removed} duplicati")
        
        # Salva Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            combined_df.to_excel(writer, index=False, sheet_name='Insights')
            
            # Formatta colonne
            worksheet = writer.sheets['Insights']
            for col_name, width in config.EXCEL_COLUMN_WIDTHS.items():
                col_idx = config.EXCEL_COLUMNS.index(col_name) + 1
                col_letter = chr(64 + col_idx)
                worksheet.column_dimensions[col_letter].width = width
        
        new_records = len(new_df) - duplicates_removed
        logger.info(f"✅ Aggiunti {new_records} nuovi record a Excel")
        logger.info(f"📊 Totale record nel file: {len(combined_df)}")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Errore salvataggio Excel: {e}")
        return False

# ==============================================================================
# FUNZIONI PER VALIDAZIONE DATI
# ==============================================================================

def validate_article_data(article: Dict[str, str]) -> bool:
    """
    Valida che un articolo abbia i campi obbligatori
    
    Args:
        article: Dizionario con dati articolo
    
    Returns:
        True se valido, False altrimenti
    """
    required_fields = ['Titolo paper', 'Fonte e società']
    
    for field in required_fields:
        if not article.get(field) or article[field].strip() == "":
            logger.warning(f"⚠️  Articolo scartato: campo '{field}' mancante")
            return False
    
    # Titolo troppo corto (probabilmente errore)
    if len(article.get('Titolo paper', '')) < 10:
        logger.warning(f"⚠️  Articolo scartato: titolo troppo corto")
        return False
    
    return True

def is_relevant_article(title: str, description: str) -> bool:
    """
    Verifica se un articolo è rilevante per tecnologie dirompenti
    
    Args:
        title: Titolo articolo
        description: Descrizione articolo
    
    Returns:
        True se rilevante
    """
    combined_text = f"{title} {description}".lower()
    return config.is_disruptive_tech_related(combined_text)

# ==============================================================================
# FUNZIONI DI UTILITÀ GENERALI
# ==============================================================================

def ensure_directory_exists(directory: str) -> bool:
    """Crea una directory se non esiste"""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"❌ Impossibile creare directory {directory}: {e}")
        return False

def get_domain(url: str) -> str:
    """Estrae il dominio da un URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return ""

def create_article_dict(
    title: str,
    source: str,
    category: str = "N/A",
    description: str = "N/A",
    article_date: str = "N/A",
    writing_date: str = None
) -> Dict[str, str]:
    """
    Crea un dizionario articolo con il formato corretto per Excel
    
    Args:
        title: Titolo articolo
        source: Fonte (nome società + URL)
        category: Argomento/categoria
        description: Descrizione breve
        article_date: Data pubblicazione
        writing_date: Data di scrittura (default oggi)
    
    Returns:
        Dizionario formattato
    """
    if writing_date is None:
        writing_date = get_today_formatted()
    
    return {
        'Giorno di scrittura': writing_date,
        'Giorno articolo': article_date if article_date else "N/A",
        'Fonte e società': source,
        'Argomento': category if category else "N/A",
        'Titolo paper': clean_text(title),
        'Descrizione': truncate_text(clean_text(description), max_length=300)
    }

def print_summary(results: Dict[str, List[Dict]]):
    """
    Stampa un riepilogo dei risultati dello scraping
    
    Args:
        results: Dizionario con risultati per ogni società
    """
    print("\n" + "="*80)
    print("📊 RIEPILOGO SCRAPING")
    print("="*80)
    
    total_articles = 0
    for site, articles in results.items():
        count = len(articles)
        total_articles += count
        status = "✅" if count > 0 else "⚠️ "
        print(f"{status} {site.upper()}: {count} articoli")
    
    print("-"*80)
    print(f"📈 TOTALE: {total_articles} articoli estratti")
    print("="*80 + "\n")

# ==============================================================================
# MAIN (per testing)
# ==============================================================================

if __name__ == '__main__':
    # Test funzioni
    logger.info("🧪 Testing modulo utils...")
    
    # Test parsing date
    test_dates = [
        "December 15, 2025",
        "15 Dec 2025",
        "2025-12-15",
        "15/12/2025"
    ]
    
    print("\n📅 Test parsing date:")
    for date_str in test_dates:
        parsed = parse_date(date_str)
        formatted = format_date(parsed)
        print(f"  {date_str:20s} → {formatted}")
    
    # Test pulizia testo
    print("\n🧹 Test pulizia testo:")
    dirty_text = "  This is   a   \n\n test   with   <html>tags</html>  "
    clean = clean_text(dirty_text)
    print(f"  Prima:  '{dirty_text}'")
    print(f"  Dopo:   '{clean}'")
    
    logger.info("✅ Test completati")
