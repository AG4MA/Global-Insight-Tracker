# -*- coding: utf-8 -*-
"""
Document Downloader - Scarica PDF e contenuti HTML dagli URL
"""

import os
import re
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

from ..core.config import OUTPUT_DIR, SCRAPING
from ..core.utils import logger, get_request_headers, slugify


# Directory per documenti scaricati
DOCS_DIR = OUTPUT_DIR.parent / "docs"
DOCS_DIR.mkdir(exist_ok=True)


class DocumentDownloader:
    """
    Scarica documenti (PDF, HTML) dagli URL degli articoli.
    
    Gestisce:
    - Download PDF diretti
    - Estrazione contenuto HTML da pagine articolo
    - Caching per evitare download duplicati
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(get_request_headers())
        self.downloaded = []
        self.failed = []
    
    def download_article(self, article: Dict) -> Dict:
        """
        Scarica contenuto di un singolo articolo.
        
        Args:
            article: Dict con almeno 'url' e 'title'
            
        Returns:
            Article aggiornato con 'content_path' e 'content_text'
        """
        url = article.get('url', '')
        title = article.get('title', 'untitled')
        
        if not url:
            return article
        
        try:
            # Genera filename unico
            filename = self._generate_filename(url, title)
            
            # Controlla se è PDF
            if self._is_pdf_url(url):
                result = self._download_pdf(url, filename)
            else:
                result = self._download_html_content(url, filename)
            
            if result:
                article['content_path'] = str(result['path'])
                article['content_text'] = result.get('text', '')[:5000]  # Limita
                article['content_type'] = result['type']
                self.downloaded.append(url)
                logger.info(f"✓ Downloaded: {title[:50]}...")
            else:
                self.failed.append(url)
                
        except Exception as e:
            logger.warning(f"✗ Failed {url}: {e}")
            self.failed.append(url)
        
        return article
    
    def download_all(self, articles: List[Dict], max_docs: int = 50) -> List[Dict]:
        """
        Scarica contenuti per lista di articoli.
        
        Args:
            articles: Lista articoli
            max_docs: Numero massimo documenti da scaricare
            
        Returns:
            Articoli aggiornati con contenuto
        """
        logger.info(f"📥 Download documenti (max {max_docs})...")
        
        for i, article in enumerate(articles[:max_docs]):
            article = self.download_article(article)
            
            # Rate limiting
            if i > 0 and i % 5 == 0:
                time.sleep(SCRAPING.request_delay)
        
        logger.info(f"✅ Downloaded: {len(self.downloaded)}, Failed: {len(self.failed)}")
        return articles
    
    def _download_pdf(self, url: str, filename: str) -> Optional[Dict]:
        """Scarica PDF"""
        try:
            response = self.session.get(url, timeout=60, stream=True)
            response.raise_for_status()
            
            # Verifica che sia davvero PDF
            content_type = response.headers.get('content-type', '')
            if 'pdf' not in content_type.lower() and not url.endswith('.pdf'):
                return self._download_html_content(url, filename)
            
            # Salva PDF
            pdf_path = DOCS_DIR / f"{filename}.pdf"
            with open(pdf_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Estrai testo
            text = self._extract_pdf_text(pdf_path)
            
            return {
                'path': pdf_path,
                'type': 'pdf',
                'text': text
            }
            
        except Exception as e:
            logger.debug(f"PDF download failed: {e}")
            return None
    
    def _download_html_content(self, url: str, filename: str) -> Optional[Dict]:
        """Scarica e estrai contenuto da pagina HTML"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Rimuovi elementi non utili
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 
                           'aside', 'iframe', 'noscript']):
                tag.decompose()
            
            # Cerca contenuto principale
            content = self._find_main_content(soup)
            
            if not content:
                return None
            
            # Salva HTML pulito
            html_path = DOCS_DIR / f"{filename}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(f"<!-- Source: {url} -->\n")
                f.write(str(content))
            
            # Estrai testo
            text = content.get_text(separator='\n', strip=True)
            
            # Salva anche testo puro
            txt_path = DOCS_DIR / f"{filename}.txt"
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"Source: {url}\n\n")
                f.write(text)
            
            return {
                'path': txt_path,
                'type': 'html',
                'text': text
            }
            
        except Exception as e:
            logger.debug(f"HTML download failed: {e}")
            return None
    
    def _find_main_content(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Trova il contenuto principale della pagina"""
        # Prova selettori comuni per contenuto articolo
        selectors = [
            'article',
            'main',
            '[role="main"]',
            '.article-content',
            '.article-body',
            '.post-content',
            '.entry-content',
            '.content-main',
            '#content',
            '.insight-content',
            '.publication-content',
        ]
        
        for selector in selectors:
            content = soup.select_one(selector)
            if content and len(content.get_text(strip=True)) > 500:
                return content
        
        # Fallback: trova il div più grande con testo
        divs = soup.find_all('div')
        if divs:
            best = max(divs, key=lambda d: len(d.get_text(strip=True)))
            if len(best.get_text(strip=True)) > 500:
                return best
        
        return soup.body if soup.body else soup
    
    def _extract_pdf_text(self, pdf_path: Path) -> str:
        """Estrae testo da PDF"""
        try:
            import PyPDF2
            
            text_parts = []
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages[:20]:  # Max 20 pagine
                    text_parts.append(page.extract_text() or '')
            
            return '\n'.join(text_parts)
            
        except ImportError:
            logger.warning("PyPDF2 non installato - pip install PyPDF2")
            return ''
        except Exception as e:
            logger.debug(f"PDF text extraction failed: {e}")
            return ''
    
    def _generate_filename(self, url: str, title: str) -> str:
        """Genera filename unico"""
        # Slug dal titolo
        slug = slugify(title)[:50]
        
        # Hash dell'URL per unicità
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        return f"{slug}_{url_hash}"
    
    def _is_pdf_url(self, url: str) -> bool:
        """Controlla se URL punta a PDF"""
        url_lower = url.lower()
        return (
            url_lower.endswith('.pdf') or
            '/pdf/' in url_lower or
            'download' in url_lower and 'pdf' in url_lower
        )
    
    def get_stats(self) -> Dict:
        """Ritorna statistiche download"""
        return {
            'downloaded': len(self.downloaded),
            'failed': len(self.failed),
            'docs_dir': str(DOCS_DIR),
        }
