# -*- coding: utf-8 -*-
"""
Enhanced Scraper - Supporto Selenium per siti JS-heavy
Global Insight Tracker v2.1
"""

import time
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

# Import opzionale Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium non disponibile - pip install selenium webdriver-manager")


class EnhancedScraper:
    """Scraper potenziato con supporto Selenium per siti JavaScript-heavy"""
    
    def __init__(self):
        self.driver = None
        
    def _get_driver(self):
        """Inizializza Chrome driver"""
        if not SELENIUM_AVAILABLE:
            raise RuntimeError("Selenium non installato")
            
        if self.driver is None:
            opts = Options()
            opts.add_argument('--headless=new')
            opts.add_argument('--disable-gpu')
            opts.add_argument('--window-size=1920,1080')
            opts.add_argument('--no-sandbox')
            opts.add_argument('--disable-dev-shm-usage')
            opts.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=opts)
            
        return self.driver
    
    def close(self):
        """Chiudi browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def fetch_with_js(self, url: str, wait_time: int = 8, scroll: bool = True) -> str:
        """
        Scarica pagina con rendering JavaScript completo
        
        Args:
            url: URL da scaricare
            wait_time: Secondi da attendere per rendering
            scroll: Se True, scrolla la pagina per caricare lazy content
            
        Returns:
            HTML completo della pagina
        """
        driver = self._get_driver()
        
        logger.info(f"Caricamento JS: {url}")
        driver.get(url)
        
        # Attendi rendering iniziale
        time.sleep(wait_time)
        
        # Scroll per caricare lazy content
        if scroll:
            for i in range(3):
                driver.execute_script(f"window.scrollTo(0, {(i+1) * 1000});")
                time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
        
        return driver.page_source
    
    def extract_insight_links(self, html: str, base_url: str, 
                               link_pattern: str = "/insights/") -> List[Dict]:
        """
        Estrae link a insight/report da HTML
        
        Args:
            html: HTML della pagina
            base_url: URL base per link relativi
            link_pattern: Pattern da cercare negli href
            
        Returns:
            Lista di dizionari con titolo, url, etc.
        """
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        seen_urls = set()
        
        # Trova tutti i link con pattern
        links = soup.find_all('a', href=lambda x: x and link_pattern in x)
        
        logger.info(f"Trovati {len(links)} link con pattern '{link_pattern}'")
        
        for link in links:
            href = link.get('href', '')
            
            # Costruisci URL completo
            if href.startswith('/'):
                full_url = base_url.rstrip('/') + href
            elif href.startswith('http'):
                full_url = href
            else:
                continue
            
            # Deduplica
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)
            
            # Estrai titolo
            title = self._extract_title(link)
            if not title or len(title) < 5:
                continue
            
            # Filtra navigazione e link generici
            skip_patterns = ['subscribe', 'newsletter', 'contact', 'about', 'login', 
                           'sign in', 'register', 'careers', 'locations', 'search']
            if any(p in title.lower() for p in skip_patterns):
                continue
            
            results.append({
                'title': title,
                'url': full_url,
                'source': self._extract_domain(base_url),
                'category': self._extract_category(href),
                'description': self._extract_description(link),
                'date': ''
            })
        
        logger.info(f"Estratti {len(results)} articoli unici")
        return results
    
    def _extract_title(self, element) -> str:
        """Estrai titolo da elemento"""
        # Prima prova testo diretto
        text = element.get_text(strip=True)
        if text and len(text) > 5:
            # Pulisci
            text = re.sub(r'\s+', ' ', text)
            return text[:200]
        
        # Cerca in elementi figli
        for child in element.find_all(['span', 'h2', 'h3', 'h4', 'p']):
            text = child.get_text(strip=True)
            if text and len(text) > 5:
                return text[:200]
        
        return ''
    
    def _extract_description(self, element) -> str:
        """Estrai descrizione"""
        parent = element.parent
        if parent:
            desc = parent.find(['p', 'span'], class_=lambda x: x and 'desc' in str(x).lower())
            if desc:
                return desc.get_text(strip=True)[:500]
        return ''
    
    def _extract_category(self, url: str) -> str:
        """Estrai categoria da URL"""
        patterns = {
            'technology': 'Technology',
            'digital': 'Digital Transformation',
            'ai': 'Artificial Intelligence',
            'data': 'Data & Analytics',
            'cloud': 'Cloud',
            'cyber': 'Cybersecurity',
            'financial': 'Financial Services',
            'healthcare': 'Healthcare',
            'consumer': 'Consumer',
            'energy': 'Energy',
            'manufacturing': 'Manufacturing'
        }
        url_lower = url.lower()
        for pattern, category in patterns.items():
            if pattern in url_lower:
                return category
        return 'General'
    
    def _extract_domain(self, url: str) -> str:
        """Estrai nome sorgente da URL"""
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        
        if 'deloitte' in domain:
            return 'Deloitte'
        elif 'pwc' in domain:
            return 'PwC'
        elif 'mckinsey' in domain:
            return 'McKinsey'
        elif 'bcg' in domain:
            return 'BCG'
        elif 'ey.' in domain or 'ey-' in domain:
            return 'EY'
        elif 'kpmg' in domain:
            return 'KPMG'
        elif 'accenture' in domain:
            return 'Accenture'
        elif 'bain' in domain:
            return 'Bain'
        elif 'gartner' in domain:
            return 'Gartner'
        elif 'forrester' in domain:
            return 'Forrester'
        elif 'idc' in domain:
            return 'IDC'
        
        return domain.split('.')[0].capitalize()


def scrape_deloitte() -> List[Dict]:
    """Scrape Deloitte Insights con Selenium"""
    scraper = EnhancedScraper()
    all_articles = []
    
    urls = [
        'https://www2.deloitte.com/us/en/insights.html',
        'https://www2.deloitte.com/us/en/insights/focus/tech-trends.html',
        'https://www2.deloitte.com/us/en/insights/topics/digital-transformation.html',
    ]
    
    try:
        for url in urls:
            try:
                html = scraper.fetch_with_js(url, wait_time=8)
                articles = scraper.extract_insight_links(
                    html, 
                    'https://www2.deloitte.com',
                    '/insights/'
                )
                all_articles.extend(articles)
                print(f"✓ {url}: {len(articles)} articoli")
            except Exception as e:
                print(f"✗ {url}: {e}")
    finally:
        scraper.close()
    
    # Deduplica per URL
    seen = set()
    unique = []
    for art in all_articles:
        if art['url'] not in seen:
            seen.add(art['url'])
            unique.append(art)
    
    return unique


def scrape_mckinsey() -> List[Dict]:
    """Scrape McKinsey Insights"""
    scraper = EnhancedScraper()
    all_articles = []
    
    urls = [
        'https://www.mckinsey.com/featured-insights',
        'https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights',
        'https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights',
    ]
    
    try:
        for url in urls:
            try:
                html = scraper.fetch_with_js(url, wait_time=8)
                articles = scraper.extract_insight_links(
                    html,
                    'https://www.mckinsey.com',
                    '/our-insights/'
                )
                # Aggiungi anche featured-insights
                articles.extend(scraper.extract_insight_links(
                    html,
                    'https://www.mckinsey.com', 
                    '/featured-insights/'
                ))
                all_articles.extend(articles)
                print(f"✓ {url}: {len(articles)} articoli")
            except Exception as e:
                print(f"✗ {url}: {e}")
    finally:
        scraper.close()
    
    # Deduplica
    seen = set()
    unique = []
    for art in all_articles:
        if art['url'] not in seen:
            seen.add(art['url'])
            unique.append(art)
    
    return unique


def scrape_bcg() -> List[Dict]:
    """Scrape BCG Insights"""
    scraper = EnhancedScraper()
    all_articles = []
    
    urls = [
        'https://www.bcg.com/publications',
        'https://www.bcg.com/capabilities/digital-technology-data',
    ]
    
    try:
        for url in urls:
            try:
                html = scraper.fetch_with_js(url, wait_time=8)
                articles = scraper.extract_insight_links(
                    html,
                    'https://www.bcg.com',
                    '/publications/'
                )
                all_articles.extend(articles)
                print(f"✓ {url}: {len(articles)} articoli")
            except Exception as e:
                print(f"✗ {url}: {e}")
    finally:
        scraper.close()
    
    # Deduplica
    seen = set()
    unique = []
    for art in all_articles:
        if art['url'] not in seen:
            seen.add(art['url'])
            unique.append(art)
    
    return unique


def main():
    """Test scraping tutte le fonti"""
    print("=" * 60)
    print("Enhanced Scraper - Test")
    print("=" * 60)
    
    all_results = []
    
    print("\n--- DELOITTE ---")
    deloitte = scrape_deloitte()
    all_results.extend(deloitte)
    print(f"Totale Deloitte: {len(deloitte)} articoli")
    for art in deloitte[:5]:
        print(f"  • {art['title'][:60]}")
    
    print("\n--- MCKINSEY ---")
    mckinsey = scrape_mckinsey()
    all_results.extend(mckinsey)
    print(f"Totale McKinsey: {len(mckinsey)} articoli")
    for art in mckinsey[:5]:
        print(f"  • {art['title'][:60]}")
    
    print("\n--- BCG ---")
    bcg = scrape_bcg()
    all_results.extend(bcg)
    print(f"Totale BCG: {len(bcg)} articoli")
    for art in bcg[:5]:
        print(f"  • {art['title'][:60]}")
    
    print("\n" + "=" * 60)
    print(f"TOTALE: {len(all_results)} articoli")
    print("=" * 60)
    
    return all_results


if __name__ == '__main__':
    main()
