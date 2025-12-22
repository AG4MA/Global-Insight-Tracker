# -*- coding: utf-8 -*-
"""
Source Crawlers - Modulo per crawler specifici per ogni fonte
Ogni crawler sa come navigare nel sito specifico e trovare i report reali

Autore: Senior Python Developer
Data: 22 Dicembre 2025
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import re
from bs4 import BeautifulSoup
import requests
import utils


class BaseCrawler(ABC):
    """Classe base per tutti i crawler site-specific"""
    
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.session = requests.Session()
        self.logger = utils.logger
    
    @abstractmethod
    def find_reports(self, max_reports: int = 10) -> List[Dict]:
        """
        Trova report sul sito. Ogni crawler implementa la sua logica.
        
        Returns:
            Lista di dizionari con:
            - title: Titolo del report
            - url: URL del report/documento
            - date: Data pubblicazione
            - topics: Lista di topic associati
            - description: Descrizione
            - document_url: URL diretto al PDF/DOCX (se disponibile)
        """
        pass
    
    @abstractmethod
    def get_document_url(self, report_url: str) -> Optional[str]:
        """
        Data una pagina di report, trova l'URL del documento scaricabile
        """
        pass
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Helper per fare richieste HTTP"""
        return utils.make_request(url)


class DeloitteCrawler(BaseCrawler):
    """Crawler specifico per Deloitte"""
    
    def __init__(self):
        super().__init__("Deloitte", "https://www2.deloitte.com")
        
        # Pagine dove Deloitte pubblica report
        self.report_sections = [
            "https://www2.deloitte.com/us/en/insights/focus/tech-trends.html",
            "https://www2.deloitte.com/us/en/insights/industry/technology.html",
            "https://www2.deloitte.com/us/en/insights/topics/digital-transformation.html",
            "https://www2.deloitte.com/us/en/insights/focus/industry-4-0.html"
        ]
    
    def find_reports(self, max_reports: int = 10) -> List[Dict]:
        """Trova report su Deloitte"""
        reports = []
        
        for section_url in self.report_sections:
            if len(reports) >= max_reports:
                break
            
            self.logger.info(f"🔍 Scanning Deloitte: {section_url}")
            response = self._make_request(section_url)
            
            if not response:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Deloitte usa vari pattern - cerchiamo link a PDF o pagine di report
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Skip navigation links
                if any(skip in href for skip in ['#', 'javascript:', 'mailto:']):
                    continue
                
                # Costruisci URL completo
                if href.startswith('/'):
                    full_url = self.base_url + href
                elif not href.startswith('http'):
                    continue
                else:
                    full_url = href
                
                # Cerchiamo pagine che probabilmente sono report
                if self._is_likely_report(link, href):
                    title = self._extract_title(link)
                    
                    if title and len(title) > 20:  # Filtro titoli troppo corti
                        report = {
                            'source': self.name,
                            'title': title,
                            'url': full_url,
                            'date': self._extract_date(link),
                            'topics': self._guess_topics(title, link),
                            'description': self._extract_description(link),
                            'document_url': None  # Verrà riempito dopo
                        }
                        
                        # Evita duplicati
                        if not any(r['url'] == full_url for r in reports):
                            reports.append(report)
                            self.logger.info(f"  ✓ Found: {title[:60]}...")
                        
                        if len(reports) >= max_reports:
                            break
            
            if len(reports) >= max_reports:
                break
        
        # Per ogni report, cerca il documento scaricabile
        for report in reports:
            report['document_url'] = self.get_document_url(report['url'])
        
        return reports
    
    def get_document_url(self, report_url: str) -> Optional[str]:
        """Trova il PDF scaricabile dalla pagina del report"""
        
        # Se è già un PDF, ritorna direttamente
        if report_url.endswith('.pdf'):
            return report_url
        
        # Altrimenti visita la pagina e cerca il PDF
        response = self._make_request(report_url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Cerca link a PDF
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '.pdf' in href.lower():
                if href.startswith('/'):
                    return self.base_url + href
                elif href.startswith('http'):
                    return href
        
        # Se non trova PDF, cerca button "Download" o simili
        download_buttons = soup.find_all(['a', 'button'], 
                                        class_=re.compile(r'download|pdf', re.I))
        for btn in download_buttons:
            if btn.get('href') and '.pdf' in btn['href']:
                href = btn['href']
                if href.startswith('/'):
                    return self.base_url + href
                elif href.startswith('http'):
                    return href
        
        return None
    
    def _is_likely_report(self, link, href: str) -> bool:
        """Determina se un link probabilmente porta a un report"""
        
        # Keywords che indicano report
        report_keywords = ['insight', 'report', 'white-paper', 'whitepaper', 
                          'research', 'study', 'analysis', 'trend', 'outlook']
        
        # Check URL
        href_lower = href.lower()
        if any(kw in href_lower for kw in report_keywords):
            return True
        
        # Check link text
        link_text = link.get_text().lower()
        if any(kw in link_text for kw in report_keywords):
            return True
        
        # Check se ha classe che indica contenuto principale
        classes = link.get('class', [])
        if any('card' in c or 'article' in c or 'insight' in c for c in classes):
            return True
        
        return False
    
    def _extract_title(self, link) -> Optional[str]:
        """Estrae titolo dal link"""
        # Prima prova il testo del link
        text = link.get_text(strip=True)
        if text and len(text) > 10:
            return text
        
        # Poi prova attributi
        if link.get('title'):
            return link['title']
        
        if link.get('aria-label'):
            return link['aria-label']
        
        return None
    
    def _extract_date(self, link) -> Optional[datetime]:
        """Cerca di estrarre data dalla pagina"""
        # Per ora ritorniamo None, verrà estratta dal documento
        return None
    
    def _extract_description(self, link) -> str:
        """Estrae descrizione se disponibile"""
        parent = link.find_parent(['div', 'article', 'section'])
        if parent:
            # Cerca paragrafi vicini
            desc = parent.find('p', class_=re.compile(r'description|summary|excerpt', re.I))
            if desc:
                return desc.get_text(strip=True)
        return ""
    
    def _guess_topics(self, title: str, link) -> List[str]:
        """Indovina i topic dal titolo e contesto"""
        topics = []
        
        title_lower = title.lower()
        
        topic_keywords = {
            'AI': ['artificial intelligence', 'ai', 'machine learning', 'ml', 'deep learning', 'neural'],
            'Quantum': ['quantum', 'qubit'],
            'Blockchain': ['blockchain', 'crypto', 'web3', 'defi', 'nft'],
            'Cloud': ['cloud', 'aws', 'azure', 'saas', 'paas'],
            'Cybersecurity': ['cyber', 'security', 'hack', 'threat', 'breach'],
            'IoT': ['iot', 'internet of things', 'sensor'],
            'Automation': ['automation', 'rpa', 'robotic process'],
            'Data Analytics': ['data', 'analytics', 'big data', 'insight'],
            'Metaverse': ['metaverse', 'virtual reality', 'vr', 'ar', 'augmented'],
            'Sustainability': ['sustainability', 'esg', 'climate', 'green'],
            'Digital Transformation': ['digital transformation', 'digitalization']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in title_lower for kw in keywords):
                topics.append(topic)
        
        # Se non trova topic, default a "Technology"
        if not topics:
            topics.append('Technology')
        
        return topics


class PwCCrawler(BaseCrawler):
    """Crawler specifico per PwC"""
    
    def __init__(self):
        super().__init__("PwC", "https://www.pwc.com")
        self.report_sections = [
            "https://www.pwc.com/gx/en/issues.html",
            "https://www.pwc.com/gx/en/services/consulting/technology.html",
            "https://www.pwc.com/us/en/library.html"
        ]
    
    def find_reports(self, max_reports: int = 10) -> List[Dict]:
        """Trova report su PwC"""
        reports = []
        
        # Logica simile a Deloitte ma adattata per PwC
        for section_url in self.report_sections:
            if len(reports) >= max_reports:
                break
            
            self.logger.info(f"🔍 Scanning PwC: {section_url}")
            response = self._make_request(section_url)
            
            if not response:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # PwC patterns
            for article in soup.find_all(['article', 'div'], class_=re.compile(r'card|item|content', re.I)):
                if len(reports) >= max_reports:
                    break
                
                link = article.find('a', href=True)
                if not link:
                    continue
                
                href = link['href']
                if href.startswith('/'):
                    full_url = self.base_url + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                
                title_elem = article.find(['h2', 'h3', 'h4'])
                if not title_elem:
                    title_elem = link
                
                title = title_elem.get_text(strip=True)
                
                if title and len(title) > 20:
                    report = {
                        'source': self.name,
                        'title': title,
                        'url': full_url,
                        'date': None,
                        'topics': self._guess_topics(title),
                        'description': self._extract_description(article),
                        'document_url': None
                    }
                    
                    if not any(r['url'] == full_url for r in reports):
                        reports.append(report)
                        self.logger.info(f"  ✓ Found: {title[:60]}...")
        
        # Cerca documenti
        for report in reports:
            report['document_url'] = self.get_document_url(report['url'])
        
        return reports
    
    def get_document_url(self, report_url: str) -> Optional[str]:
        """Trova documento su PwC"""
        if report_url.endswith('.pdf'):
            return report_url
        
        response = self._make_request(report_url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Cerca PDF
        for link in soup.find_all('a', href=True):
            if '.pdf' in link['href'].lower():
                href = link['href']
                if href.startswith('/'):
                    return self.base_url + href
                elif href.startswith('http'):
                    return href
        
        return None
    
    def _extract_description(self, article) -> str:
        """Estrae descrizione"""
        desc = article.find('p')
        if desc:
            return desc.get_text(strip=True)[:300]
        return ""
    
    def _guess_topics(self, title: str) -> List[str]:
        """Indovina topic"""
        topics = []
        title_lower = title.lower()
        
        topic_keywords = {
            'AI': ['artificial intelligence', 'ai ', 'machine learning', 'ml'],
            'Quantum': ['quantum'],
            'Blockchain': ['blockchain', 'crypto', 'web3'],
            'Cloud': ['cloud'],
            'Cybersecurity': ['cyber', 'security'],
            'ESG': ['esg', 'sustainability', 'climate']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in title_lower for kw in keywords):
                topics.append(topic)
        
        if not topics:
            topics.append('Business')
        
        return topics


# ==============================================================================
# FACTORY PER CREARE CRAWLER
# ==============================================================================

def get_crawler(source_name: str) -> Optional[BaseCrawler]:
    """
    Factory function per ottenere il crawler appropriato
    
    Args:
        source_name: Nome della fonte (es. 'deloitte', 'pwc')
    
    Returns:
        Istanza del crawler o None
    """
    crawlers = {
        'deloitte': DeloitteCrawler,
        'pwc': PwCCrawler,
        # Aggiungi altri crawler qui
    }
    
    crawler_class = crawlers.get(source_name.lower())
    if crawler_class:
        return crawler_class()
    
    return None


def get_all_crawlers() -> List[BaseCrawler]:
    """Ritorna lista di tutti i crawler disponibili"""
    return [
        DeloitteCrawler(),
        PwCCrawler(),
        # Aggiungi altri
    ]
