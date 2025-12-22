# -*- coding: utf-8 -*-
"""
Selenium Scraper - Scraper con supporto JavaScript rendering
"""

import time
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from ..core.config import SELENIUM, SourceConfig
from ..core.utils import (
    logger, create_article, deduplicate_articles, 
    normalize_url, extract_category_from_url
)
from .base_scraper import BaseScraper


# Import opzionale Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class SeleniumScraper(BaseScraper):
    """
    Scraper con supporto Selenium per siti JavaScript-heavy
    
    Usa Chrome headless per renderizzare JavaScript e estrarre contenuto.
    """
    
    def __init__(self, source: SourceConfig):
        super().__init__(source)
        self.driver = None
    
    def _init_driver(self):
        """Inizializza Chrome driver"""
        if not SELENIUM_AVAILABLE:
            raise RuntimeError(
                "Selenium non installato. "
                "Installa con: pip install selenium webdriver-manager"
            )
        
        if self.driver is None:
            opts = Options()
            for opt in SELENIUM.chrome_options:
                opts.add_argument(opt)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=opts)
            self.driver.set_page_load_timeout(SELENIUM.page_load_timeout)
    
    def scrape(self, max_articles: int = None) -> List[Dict]:
        """
        Scrape con Selenium
        
        Args:
            max_articles: Numero massimo articoli
            
        Returns:
            Lista articoli
        """
        if max_articles is None:
            max_articles = 10
        
        all_articles = []
        
        # URL da scrapare
        urls = [self.source.insights_url] + self.source.alternative_urls[:2]
        
        try:
            self._init_driver()
            
            for url in urls:
                try:
                    articles = self._scrape_url(url)
                    all_articles.extend(articles)
                    logger.info(f"✓ {url}: {len(articles)} articoli")
                    
                    if len(all_articles) >= max_articles * 2:
                        break
                        
                except Exception as e:
                    logger.warning(f"✗ {url}: {e}")
                
        finally:
            self.close()
        
        # Deduplica e limita
        unique = deduplicate_articles(all_articles)
        return unique[:max_articles]
    
    def _scrape_url(self, url: str) -> List[Dict]:
        """Scrape singolo URL"""
        html = self.fetch_with_js(url)
        soup = self.parse_html(html)
        return self.extract_links(soup, self.source.link_pattern)
    
    def fetch_with_js(self, url: str, wait_time: int = None, scroll: bool = True) -> str:
        """
        Scarica pagina con rendering JavaScript
        
        Args:
            url: URL da scaricare
            wait_time: Secondi attesa rendering
            scroll: Se scrollare per lazy loading
            
        Returns:
            HTML renderizzato
        """
        if wait_time is None:
            wait_time = 8
        
        self._init_driver()
        
        logger.info(f"Caricamento JS: {url}")
        self.driver.get(url)
        
        # Attendi rendering
        time.sleep(wait_time)
        
        # Scroll per lazy loading
        if scroll:
            self._scroll_page()
        
        return self.driver.page_source
    
    def _scroll_page(self):
        """Scrolla pagina per caricare lazy content"""
        for i in range(3):
            self.driver.execute_script(f"window.scrollTo(0, {(i+1) * 1000});")
            time.sleep(0.5)
        
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        self.driver.execute_script("window.scrollTo(0, 0);")
    
    def close(self):
        """Chiude browser e risorse"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
        super().close()
