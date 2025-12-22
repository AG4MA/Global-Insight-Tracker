# -*- coding: utf-8 -*-
"""
Global Insight Tracker - Main Script
Sistema automatizzato per monitorare white papers e insights su tecnologie dirompenti
dalle principali società di consulenza globali

Autore: Senior Python Developer
Data: 22 Dicembre 2025
"""

import os
import sys
import argparse
from typing import List, Dict, Optional
from datetime import datetime

from bs4 import BeautifulSoup

# Import moduli locali
import config
import utils

# ==============================================================================
# FUNZIONI DI SCRAPING PER OGNI SOCIETÀ
# ==============================================================================

def scrape_generic_site(site_key: str, max_articles: int = None) -> List[Dict[str, str]]:
    """
    Funzione generica per scraping di un sito di consulenza
    
    Args:
        site_key: Chiave del sito in config.SITES_CONFIG
        max_articles: Numero massimo di articoli da estrarre
    
    Returns:
        Lista di dizionari con dati articoli
    """
    if max_articles is None:
        max_articles = config.MAX_ARTICLES_PER_SITE
    
    # Ottieni configurazione sito
    site_config = config.get_site_config(site_key)
    if not site_config:
        utils.logger.error(f"❌ Configurazione non trovata per {site_key}")
        return []
    
    utils.logger.info(f"\n{'='*80}")
    utils.logger.info(f"🔍 Inizio scraping: {site_config['name'].upper()}")
    utils.logger.info(f"{'='*80}")
    
    articles = []
    
    # Prova URL principale
    articles.extend(_scrape_url(site_config, site_config['insights_url'], max_articles))
    
    # Se non abbastanza articoli, prova URL alternativi
    if len(articles) < max_articles and site_config.get('alternative_urls'):
        remaining = max_articles - len(articles)
        utils.logger.info(f"ℹ️  Cercando altri {remaining} articoli in URL alternativi...")
        
        for alt_url in site_config['alternative_urls']:
            if len(articles) >= max_articles:
                break
            
            new_articles = _scrape_url(site_config, alt_url, remaining)
            articles.extend(new_articles)
            remaining = max_articles - len(articles)
    
    utils.logger.info(f"✅ Scraping {site_config['name']} completato: {len(articles)} articoli")
    return articles

def _scrape_url(site_config: Dict, url: str, max_articles: int) -> List[Dict[str, str]]:
    """
    Scraping di un singolo URL
    
    Args:
        site_config: Configurazione del sito
        url: URL da scrapare
        max_articles: Numero massimo di articoli
    
    Returns:
        Lista di articoli estratti
    """
    articles = []
    
    try:
        # Effettua richiesta HTTP
        response = utils.make_request(url)
        if not response:
            return articles
        
        # Parsa HTML
        soup = utils.parse_html(response.text)
        if not soup:
            return articles
        
        # Estrai selettori dalla config
        selectors = site_config['selectors']
        
        # Trova containers degli articoli
        article_containers = utils.find_elements_by_selectors(
            soup,
            selectors['article_container'],
            limit=max_articles
        )
        
        if not article_containers:
            utils.logger.warning(f"⚠️  Nessun articolo trovato in {url}")
            utils.logger.warning(f"   Selettore usato: {selectors['article_container']}")
            return articles
        
        utils.logger.info(f"📦 Trovati {len(article_containers)} containers di articoli")
        
        # Estrai dati da ogni articolo
        for idx, container in enumerate(article_containers[:max_articles], 1):
            try:
                article_data = _extract_article_data(container, site_config, url)
                
                if article_data and utils.validate_article_data(article_data):
                    # Verifica rilevanza (opzionale)
                    if utils.is_relevant_article(
                        article_data['Titolo paper'],
                        article_data['Descrizione']
                    ):
                        articles.append(article_data)
                        utils.logger.info(f"  ✓ Articolo {idx}: {article_data['Titolo paper'][:60]}...")
                    else:
                        utils.logger.debug(f"  ⊗ Articolo {idx} non rilevante per disruptive tech")
                else:
                    utils.logger.warning(f"  ✗ Articolo {idx} scartato (dati incompleti)")
            
            except Exception as e:
                utils.logger.error(f"  ❌ Errore parsing articolo {idx}: {e}")
                continue
    
    except Exception as e:
        utils.logger.error(f"❌ Errore durante scraping di {url}: {e}")
    
    return articles

def _extract_article_data(container, site_config: Dict, base_url: str) -> Optional[Dict[str, str]]:
    """
    Estrae dati da un singolo container di articolo
    
    Args:
        container: Elemento BeautifulSoup con l'articolo
        site_config: Configurazione del sito
        base_url: URL base per link relativi
    
    Returns:
        Dizionario con dati articolo o None
    """
    selectors = site_config['selectors']
    
    # Estrai titolo
    title_elem = utils.find_element_by_selectors(container, selectors['title'])
    title = utils.extract_text(title_elem)
    
    if not title:
        return None
    
    # Estrai link
    link_elem = utils.find_element_by_selectors(container, selectors['link'])
    if not link_elem:
        link_elem = title_elem  # A volte il titolo stesso è il link
    article_url = utils.extract_link(link_elem, base_url)
    
    # Estrai data
    date_elem = utils.find_element_by_selectors(container, selectors['date'])
    date_str = utils.extract_text(date_elem)
    date_obj = utils.parse_date(date_str, site_config.get('date_format'))
    article_date = utils.format_date(date_obj)
    
    # Estrai categoria
    category_elem = utils.find_element_by_selectors(container, selectors['category'])
    category = utils.extract_text(category_elem)
    
    # Estrai descrizione
    desc_elem = utils.find_element_by_selectors(container, selectors['description'])
    description = utils.extract_text(desc_elem)
    
    # Se descrizione mancante, usa titolo
    if not description:
        description = title
    
    # Crea stringa fonte
    source = f"{site_config['name']} - {site_config['base_url']}"
    if article_url:
        source = f"{site_config['name']} - {article_url}"
    
    # Crea dizionario articolo
    return utils.create_article_dict(
        title=title,
        source=source,
        category=category,
        description=description,
        article_date=article_date
    )

# ==============================================================================
# SCRAPING CON SELENIUM (per siti dinamici)
# ==============================================================================

def scrape_with_selenium(site_key: str, max_articles: int = None) -> List[Dict[str, str]]:
    """
    Scraping usando Selenium per siti con contenuto dinamico (AJAX)
    
    Args:
        site_key: Chiave del sito
        max_articles: Numero massimo di articoli
    
    Returns:
        Lista di articoli estratti
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        
    except ImportError:
        utils.logger.error("❌ Selenium non installato. Installa con: pip install selenium webdriver-manager")
        return []
    
    if max_articles is None:
        max_articles = config.MAX_ARTICLES_PER_SITE
    
    site_config = config.get_site_config(site_key)
    if not site_config:
        return []
    
    utils.logger.info(f"🌐 Avvio browser headless per {site_config['name']}...")
    
    # Configura Chrome options
    chrome_options = Options()
    if config.SELENIUM_CONFIG['headless']:
        chrome_options.add_argument('--headless')
    
    for option in config.SELENIUM_CONFIG['chrome_options']:
        chrome_options.add_argument(option)
    
    driver = None
    articles = []
    
    try:
        # Inizializza driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.set_page_load_timeout(config.SELENIUM_CONFIG['page_load_timeout'])
        driver.implicitly_wait(config.SELENIUM_CONFIG['implicit_wait'])
        
        # Carica pagina
        url = site_config['insights_url']
        utils.logger.info(f"📄 Caricamento pagina: {url}")
        driver.get(url)
        
        # Attendi caricamento contenuto dinamico
        try:
            selectors = site_config['selectors']
            first_selector = selectors['article_container'].split(',')[0].strip()
            
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, first_selector))
            )
        except Exception:
            utils.logger.warning("⏱️  Timeout attesa elementi, proseguo comunque...")
        
        # Scroll per caricare lazy content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        import time
        time.sleep(2)
        
        # Estrai HTML e processa con BeautifulSoup
        html = driver.page_source
        soup = utils.parse_html(html)
        
        if soup:
            # Usa la stessa logica di scraping standard
            articles = _scrape_url(site_config, url, max_articles)
        
    except Exception as e:
        utils.logger.error(f"❌ Errore Selenium per {site_key}: {e}")
    
    finally:
        if driver:
            driver.quit()
            utils.logger.info("🔚 Browser chiuso")
    
    return articles

# ==============================================================================
# FUNZIONE PRINCIPALE
# ==============================================================================

def main(companies: List[str] = None, max_articles: int = None, output_file: str = None, verbose: bool = False):
    """
    Funzione principale per eseguire lo scraping
    
    Args:
        companies: Lista di società da scrapare (None = tutte)
        max_articles: Numero massimo di articoli per sito
        output_file: Nome file Excel di output
        verbose: Modalità verbose per logging
    """
    # Setup
    if verbose:
        config.LOG_LEVEL = 'DEBUG'
        utils.logger.setLevel('DEBUG')
    
    utils.logger.info("\n")
    utils.logger.info("🚀 Global Insight Tracker - AVVIO SISTEMA")
    utils.logger.info(f"⏰ Data/Ora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    utils.logger.info(f"📁 Directory: {config.BASE_DIR}")
    
    # Valida configurazione
    if not config.validate_config():
        utils.logger.error("❌ Errori di configurazione. Uscita.")
        return 1
    
    # Determina società da scrapare
    if companies:
        target_companies = [c.lower() for c in companies if c.lower() in config.SITES_CONFIG]
        if not target_companies:
            utils.logger.error(f"❌ Nessuna società valida specificata: {companies}")
            return 1
    else:
        target_companies = list(config.SITES_CONFIG.keys())
    
    utils.logger.info(f"🎯 Società target: {', '.join([c.upper() for c in target_companies])}")
    
    if max_articles is None:
        max_articles = config.MAX_ARTICLES_PER_SITE
    
    utils.logger.info(f"📊 Articoli per sito: {max_articles}")
    
    # Scraping
    all_articles = {}
    
    for company in target_companies:
        site_config = config.get_site_config(company)
        
        # Usa Selenium se richiesto
        if site_config.get('requires_selenium'):
            articles = scrape_with_selenium(company, max_articles)
        else:
            articles = scrape_generic_site(company, max_articles)
        
        all_articles[company] = articles
    
    # Stampa riepilogo
    utils.print_summary(all_articles)
    
    # Prepara dati per Excel
    flat_articles = []
    for company, articles in all_articles.items():
        flat_articles.extend(articles)
    
    if not flat_articles:
        utils.logger.warning("⚠️  Nessun articolo estratto. Verifica selettori CSS in config.py")
        return 0
    
    # Salva su Excel
    if output_file is None:
        output_file = config.OUTPUT_FILENAME
    
    output_path = os.path.join(config.OUTPUT_DIR, output_file)
    
    utils.logger.info(f"\n💾 Salvataggio dati in: {output_path}")
    
    success = utils.append_to_excel(output_path, flat_articles)
    
    if success:
        utils.logger.info(f"\n✅ PROCESSO COMPLETATO CON SUCCESSO")
        utils.logger.info(f"📄 File Excel: {output_path}")
        utils.logger.info(f"📝 Log salvato in: {os.path.join(config.LOG_DIR, config.LOG_FILENAME)}")
        return 0
    else:
        utils.logger.error(f"\n❌ ERRORE NEL SALVATAGGIO DEL FILE")
        return 1

# ==============================================================================
# CLI INTERFACE
# ==============================================================================

def parse_arguments():
    """Parsa argomenti da linea di comando"""
    parser = argparse.ArgumentParser(
        description='Global Insight Tracker - Monitor per White Papers su Tecnologie Dirompenti',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi di utilizzo:
  python main.py
  python main.py --max-articles 10
  python main.py --companies deloitte pwc ey
  python main.py --output report_2025.xlsx --verbose
        """
    )
    
    parser.add_argument(
        '--companies',
        nargs='+',
        choices=['deloitte', 'pwc', 'ey', 'kpmg', 'mckinsey', 'bcg'],
        help='Specifica quali società scrapare (default: tutte)'
    )
    
    parser.add_argument(
        '--max-articles',
        type=int,
        default=config.MAX_ARTICLES_PER_SITE,
        help=f'Numero massimo di articoli per sito (default: {config.MAX_ARTICLES_PER_SITE})'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=config.OUTPUT_FILENAME,
        help=f'Nome file Excel di output (default: {config.OUTPUT_FILENAME})'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Abilita logging dettagliato (DEBUG level)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Global Insight Tracker v1.0.0'
    )
    
    return parser.parse_args()

# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == '__main__':
    try:
        args = parse_arguments()
        
        exit_code = main(
            companies=args.companies,
            max_articles=args.max_articles,
            output_file=args.output,
            verbose=args.verbose
        )
        
        sys.exit(exit_code)
    
    except KeyboardInterrupt:
        utils.logger.warning("\n\n⚠️  Interruzione da utente (Ctrl+C)")
        sys.exit(130)
    
    except Exception as e:
        utils.logger.error(f"\n❌ ERRORE FATALE: {e}")
        import traceback
        utils.logger.error(traceback.format_exc())
        sys.exit(1)
