# -*- coding: utf-8 -*-
"""
Base Scraper - Classe base per tutti gli scraper
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from ..core.config import SCRAPING, SourceConfig
from ..core.utils import (
    logger, get_request_headers, normalize_url, 
    create_article, deduplicate_articles, extract_category_from_url
)


class BaseScraper(ABC):
    """
    Classe base astratta per tutti gli scraper
    
    Implementa logica comune e definisce interfaccia per sottoclassi.
    """
    
    def __init__(self, source: SourceConfig):
        """
        Inizializza scraper
        
        Args:
            source: Configurazione della fonte
        """
        self.source = source
        self.session = requests.Session()
        self.session.headers.update(get_request_headers())
    
    @abstractmethod
    def scrape(self, max_articles: int = None) -> List[Dict]:
        """
        Esegue scraping della fonte
        
        Args:
            max_articles: Numero massimo articoli
            
        Returns:
            Lista articoli estratti
        """
        pass
    
    def fetch_html(self, url: str, timeout: int = None) -> Optional[str]:
        """
        Scarica HTML da URL
        
        Args:
            url: URL da scaricare
            timeout: Timeout richiesta
            
        Returns:
            HTML o None se errore
        """
        if timeout is None:
            timeout = SCRAPING.request_timeout
        
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Errore fetch {url}: {e}")
            return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """Parsa HTML in BeautifulSoup"""
        return BeautifulSoup(html, 'html.parser')
    
    def extract_links(self, soup: BeautifulSoup, pattern: str) -> List[Dict]:
        """
        Estrae link che matchano pattern
        
        Args:
            soup: BeautifulSoup object
            pattern: Pattern da cercare in href
            
        Returns:
            Lista articoli con title, url, etc.
        """
        articles = []
        seen_urls = set()
        
        links = soup.find_all('a', href=lambda x: x and pattern in x)
        
        for link in links:
            href = link.get('href', '')
            url = normalize_url(href, self.source.base_url)
            
            # Skip duplicati
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            # Estrai titolo
            title = self._extract_title(link)
            if not title or len(title) < 5:
                continue
            
            # Skip link navigazione
            if self._is_navigation_link(title):
                continue
            
            articles.append(create_article(
                title=title,
                url=url,
                source=self.source.name,
                category=extract_category_from_url(url),
                description=self._extract_description(link),
            ))
        
        return articles
    
    def _extract_title(self, element) -> str:
        """Estrae titolo da elemento link"""
        # Prova testo diretto
        text = element.get_text(strip=True)
        if text and len(text) > 5:
            return text[:200]
        
        # Cerca in elementi figli
        for child in element.find_all(['span', 'h2', 'h3', 'h4', 'p']):
            text = child.get_text(strip=True)
            if text and len(text) > 5:
                return text[:200]
        
        return ''
    
    def _extract_description(self, element) -> str:
        """Estrae descrizione dal parent"""
        parent = element.parent
        if parent:
            desc = parent.find(['p', 'span'], 
                              class_=lambda x: x and 'desc' in str(x).lower())
            if desc:
                return desc.get_text(strip=True)[:500]
        return ''
    
    def _is_navigation_link(self, title: str) -> bool:
        """Verifica se è un link di navigazione"""
        skip_patterns = [
            'subscribe', 'newsletter', 'contact', 'about', 
            'login', 'sign in', 'register', 'careers', 
            'locations', 'search', 'cookie', 'privacy',
            'terms', 'legal', 'sitemap', 'more insights',
        ]
        title_lower = title.lower()
        return any(p in title_lower for p in skip_patterns)
    
    def delay(self):
        """Attende tra richieste"""
        time.sleep(SCRAPING.request_delay)
    
    def close(self):
        """Chiude risorse"""
        self.session.close()
