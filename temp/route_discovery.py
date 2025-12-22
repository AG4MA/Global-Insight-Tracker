# -*- coding: utf-8 -*-
"""
Route Discovery - Sistema di auto-discovery per mappare la struttura dei siti
Naviga automaticamente i siti per scoprire dove sono i report

Autore: Senior Python Developer
Data: 23 Dicembre 2025
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse
from collections import deque
from datetime import datetime

from bs4 import BeautifulSoup
import requests

from site_graph import SiteGraph, GraphNode, NodeType, SiteGraphRegistry
import utils


class RouteDiscovery:
    """
    Scopre automaticamente la struttura di un sito web.
    Mappa i percorsi verso i report e documenti.
    """
    
    # Pattern per identificare tipi di pagine
    REPORT_PATTERNS = [
        r'/insights?/', r'/research/', r'/reports?/', r'/publications?/',
        r'/whitepapers?/', r'/white-papers?/', r'/studies/', r'/analysis/',
        r'/thought-leadership/', r'/perspectives?/', r'/articles?/'
    ]
    
    DOCUMENT_PATTERNS = [
        r'\.pdf$', r'\.docx?$', r'\.pptx?$', r'\.xlsx?$'
    ]
    
    # Keywords per topic detection
    TOPIC_KEYWORDS = {
        'AI': ['artificial intelligence', 'ai ', ' ai', 'machine learning', 'ml ', ' ml',
               'deep learning', 'neural', 'generative ai', 'genai', 'chatgpt', 'llm'],
        'Quantum': ['quantum', 'qubit'],
        'Blockchain': ['blockchain', 'crypto', 'web3', 'defi', 'nft', 'distributed ledger'],
        'Cloud': ['cloud', 'aws', 'azure', 'gcp', 'saas', 'paas', 'iaas', 'multicloud'],
        'Cybersecurity': ['cyber', 'security', 'threat', 'breach', 'ransomware', 'zero trust'],
        'IoT': ['iot', 'internet of things', 'sensor', 'connected device', 'smart device'],
        'Data': ['data analytics', 'big data', 'data science', 'business intelligence'],
        'Digital Transformation': ['digital transformation', 'digitalization', 'digital strategy'],
        'Automation': ['automation', 'rpa', 'robotic process', 'hyperautomation'],
        'ESG': ['esg', 'sustainability', 'climate', 'carbon', 'green', 'net zero'],
        'Metaverse': ['metaverse', 'virtual reality', 'vr', 'ar', 'augmented reality', 'xr'],
        '5G': ['5g', '6g', 'wireless', 'telecom'],
        'Edge': ['edge computing', 'edge ai', 'fog computing'],
    }
    
    def __init__(self, max_depth: int = 3, max_pages: int = 100):
        """
        Args:
            max_depth: Massima profondità di navigazione dalla homepage
            max_pages: Massimo numero di pagine da visitare
        """
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.logger = utils.logger
        
        # Session per richieste
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': utils.get_random_user_agent()
        })
    
    def discover_site(self, site_name: str, start_url: str, 
                      existing_graph: Optional[SiteGraph] = None) -> SiteGraph:
        """
        Scopre la struttura di un sito partendo da URL iniziale
        
        Args:
            site_name: Nome del sito
            start_url: URL da cui iniziare (homepage o sezione)
            existing_graph: Grafo esistente da aggiornare (opzionale)
        
        Returns:
            SiteGraph con la struttura scoperta
        """
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"🔍 ROUTE DISCOVERY: {site_name}")
        self.logger.info(f"   Starting URL: {start_url}")
        self.logger.info(f"   Max depth: {self.max_depth}, Max pages: {self.max_pages}")
        self.logger.info(f"{'='*80}\n")
        
        # Crea o usa grafo esistente
        base_url = self._get_base_url(start_url)
        
        if existing_graph:
            graph = existing_graph
        else:
            graph = SiteGraph(site_name, base_url)
        
        # BFS per esplorare il sito
        visited: Set[str] = set()
        queue = deque([(start_url, 0, None)])  # (url, depth, parent_url)
        
        pages_visited = 0
        
        while queue and pages_visited < self.max_pages:
            current_url, depth, parent_url = queue.popleft()
            
            # Normalizza URL
            current_url = self._normalize_url(current_url, base_url)
            
            # Skip se già visitato o troppo profondo
            if current_url in visited or depth > self.max_depth:
                continue
            
            # Skip URL esterni
            if not self._is_same_domain(current_url, base_url):
                continue
            
            visited.add(current_url)
            pages_visited += 1
            
            self.logger.info(f"  [{pages_visited}/{self.max_pages}] Depth {depth}: {current_url[:80]}")
            
            # Visita pagina
            page_data = self._fetch_page(current_url)
            
            if not page_data:
                continue
            
            # Classifica nodo
            node = self._classify_page(current_url, page_data, depth, parent_url)
            graph.add_node(node)
            
            # Aggiungi edge da parent
            if parent_url:
                graph.add_edge(parent_url, current_url)
            
            # Registra rotte se è un tipo importante
            if node.node_type == NodeType.LISTING:
                graph.register_report_route('reports', current_url)
            elif node.node_type == NodeType.DOCUMENT:
                graph.register_report_route('documents', current_url)
            
            # Estrai link da seguire
            links = self._extract_links(current_url, page_data['soup'], base_url)
            
            for link_url, link_text in links:
                if link_url not in visited:
                    queue.append((link_url, depth + 1, current_url))
                    
                    # Aggiungi edge anche se non ancora visitato
                    graph.add_edge(current_url, link_url, link_text)
        
        self.logger.info(f"\n✅ Discovery completata: {len(graph.nodes)} nodi, {len(graph.edges)} edges")
        self.logger.info(f"   Topics trovati: {graph.site_topics}")
        
        return graph
    
    def quick_scan(self, site_name: str, urls: List[str]) -> SiteGraph:
        """
        Scan veloce di URL specifici (senza navigazione profonda)
        Utile per mappare velocemente sezioni note
        
        Args:
            site_name: Nome del sito
            urls: Lista di URL da scansionare
        
        Returns:
            SiteGraph
        """
        self.logger.info(f"\n🚀 QUICK SCAN: {site_name} - {len(urls)} URLs\n")
        
        base_url = self._get_base_url(urls[0]) if urls else ""
        graph = SiteGraph(site_name, base_url)
        
        for url in urls:
            self.logger.info(f"  Scanning: {url[:70]}")
            
            page_data = self._fetch_page(url)
            
            if page_data:
                node = self._classify_page(url, page_data, depth=1, parent_url=None)
                graph.add_node(node)
                
                # Estrai documenti dalla pagina
                docs = self._find_documents(url, page_data['soup'], base_url)
                
                for doc_url, doc_text in docs:
                    doc_node = GraphNode(
                        url=doc_url,
                        node_type=NodeType.DOCUMENT,
                        title=doc_text or "Document",
                        topics=self._detect_topics(doc_text),
                        depth=2,
                        parent_url=url,
                        document_url=doc_url
                    )
                    graph.add_node(doc_node)
                    graph.add_edge(url, doc_url, doc_text, "download")
                    graph.register_report_route('documents', doc_url)
                    
                    self.logger.info(f"    📄 Found: {doc_text[:50] if doc_text else doc_url[-30:]}")
        
        return graph
    
    def _fetch_page(self, url: str) -> Optional[Dict]:
        """Scarica pagina e ritorna soup + metadata"""
        try:
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Estrai metadata base
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
            
            return {
                'soup': soup,
                'title': title,
                'content_type': response.headers.get('content-type', ''),
                'status': response.status_code
            }
        
        except Exception as e:
            self.logger.debug(f"    ⚠️ Errore fetch {url}: {e}")
            return None
    
    def _classify_page(self, url: str, page_data: Dict, depth: int, 
                       parent_url: Optional[str]) -> GraphNode:
        """Classifica tipo di pagina"""
        
        soup = page_data['soup']
        title = page_data['title']
        url_lower = url.lower()
        
        # Determina tipo
        node_type = NodeType.UNKNOWN
        
        # È un documento?
        for pattern in self.DOCUMENT_PATTERNS:
            if re.search(pattern, url_lower):
                node_type = NodeType.DOCUMENT
                break
        
        # È una pagina di report?
        if node_type == NodeType.UNKNOWN:
            for pattern in self.REPORT_PATTERNS:
                if re.search(pattern, url_lower):
                    # Check se è listing o singola
                    article_count = len(soup.find_all(['article', 'div'], 
                                        class_=re.compile(r'card|item|article|post', re.I)))
                    
                    if article_count > 3:
                        node_type = NodeType.LISTING
                    else:
                        node_type = NodeType.REPORT_PAGE
                    break
        
        # È homepage?
        if node_type == NodeType.UNKNOWN:
            parsed = urlparse(url)
            if parsed.path in ['/', '', '/en', '/us', '/en-us']:
                node_type = NodeType.HOME
        
        # Default a sezione
        if node_type == NodeType.UNKNOWN:
            node_type = NodeType.SECTION
        
        # Detect topics
        page_text = soup.get_text().lower()
        topics = self._detect_topics(page_text)
        
        # Trova documento se presente
        document_url = None
        if node_type == NodeType.REPORT_PAGE:
            docs = self._find_documents(url, soup, self._get_base_url(url))
            if docs:
                document_url = docs[0][0]  # Primo documento trovato
        
        return GraphNode(
            url=url,
            node_type=node_type,
            title=title,
            topics=topics,
            depth=depth,
            parent_url=parent_url,
            document_url=document_url,
            last_visited=datetime.now().isoformat(),
            visit_count=1
        )
    
    def _detect_topics(self, text: str) -> List[str]:
        """Rileva topics dal testo"""
        text_lower = text.lower()
        topics = []
        
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic)
        
        return topics
    
    def _extract_links(self, page_url: str, soup: BeautifulSoup, 
                       base_url: str) -> List[Tuple[str, str]]:
        """Estrae link rilevanti dalla pagina"""
        links = []
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            link_text = a.get_text(strip=True)[:100]  # Max 100 char
            
            # Skip non-navigabili
            if any(skip in href for skip in ['#', 'javascript:', 'mailto:', 'tel:']):
                continue
            
            # Costruisci URL completo
            full_url = self._normalize_url(href, base_url)
            
            # Solo link interni e rilevanti
            if self._is_same_domain(full_url, base_url):
                # Prioritizza link che sembrano report
                is_interesting = any(
                    re.search(pattern, full_url.lower())
                    for pattern in self.REPORT_PATTERNS + self.DOCUMENT_PATTERNS
                )
                
                if is_interesting:
                    links.insert(0, (full_url, link_text))  # Priorità alta
                else:
                    links.append((full_url, link_text))
        
        return links[:50]  # Limita a 50 link per pagina
    
    def _find_documents(self, page_url: str, soup: BeautifulSoup, 
                        base_url: str) -> List[Tuple[str, str]]:
        """Trova link a documenti scaricabili"""
        documents = []
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            
            for pattern in self.DOCUMENT_PATTERNS:
                if re.search(pattern, href.lower()):
                    full_url = self._normalize_url(href, base_url)
                    link_text = a.get_text(strip=True) or a.get('title', '')
                    documents.append((full_url, link_text))
                    break
        
        return documents
    
    def _normalize_url(self, url: str, base_url: str) -> str:
        """Normalizza URL"""
        if url.startswith('http'):
            return url.split('#')[0].split('?')[0]
        else:
            return urljoin(base_url, url).split('#')[0].split('?')[0]
    
    def _get_base_url(self, url: str) -> str:
        """Estrae base URL"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def _is_same_domain(self, url: str, base_url: str) -> bool:
        """Verifica se URL è dello stesso dominio"""
        try:
            url_domain = urlparse(url).netloc
            base_domain = urlparse(base_url).netloc
            
            # Gestisci www
            url_domain = url_domain.replace('www.', '')
            base_domain = base_domain.replace('www.', '')
            
            return url_domain == base_domain
        except:
            return False


# ==============================================================================
# PRESET ROTTE CONOSCIUTE PER SITI PRINCIPALI
# ==============================================================================

KNOWN_SITE_ROUTES = {
    'deloitte': {
        'base_url': 'https://www2.deloitte.com',
        'entry_points': [
            'https://www2.deloitte.com/us/en/insights.html',
            'https://www2.deloitte.com/us/en/insights/focus/tech-trends.html',
            'https://www2.deloitte.com/us/en/insights/topics/digital-transformation.html',
            'https://www2.deloitte.com/us/en/insights/industry/technology.html'
        ]
    },
    'pwc': {
        'base_url': 'https://www.pwc.com',
        'entry_points': [
            'https://www.pwc.com/gx/en/issues.html',
            'https://www.pwc.com/gx/en/issues/technology.html',
            'https://www.pwc.com/us/en/library.html'
        ]
    },
    'mckinsey': {
        'base_url': 'https://www.mckinsey.com',
        'entry_points': [
            'https://www.mckinsey.com/featured-insights',
            'https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights',
            'https://www.mckinsey.com/mgi/overview'
        ]
    },
    'bcg': {
        'base_url': 'https://www.bcg.com',
        'entry_points': [
            'https://www.bcg.com/publications',
            'https://www.bcg.com/capabilities/digital-technology-data'
        ]
    },
    'bain': {
        'base_url': 'https://www.bain.com',
        'entry_points': [
            'https://www.bain.com/insights/',
            'https://www.bain.com/insights/topics/technology/'
        ]
    },
    'accenture': {
        'base_url': 'https://www.accenture.com',
        'entry_points': [
            'https://www.accenture.com/us-en/insights',
            'https://www.accenture.com/us-en/insights/technology-index'
        ]
    },
    'gartner': {
        'base_url': 'https://www.gartner.com',
        'entry_points': [
            'https://www.gartner.com/en/articles',
            'https://www.gartner.com/en/information-technology/insights'
        ]
    },
    'forrester': {
        'base_url': 'https://www.forrester.com',
        'entry_points': [
            'https://www.forrester.com/research/',
            'https://www.forrester.com/blogs/'
        ]
    },
    'kpmg': {
        'base_url': 'https://kpmg.com',
        'entry_points': [
            'https://kpmg.com/xx/en/home/insights.html',
            'https://kpmg.com/xx/en/home/insights/technology.html'
        ]
    },
    'ey': {
        'base_url': 'https://www.ey.com',
        'entry_points': [
            'https://www.ey.com/en_gl/insights',
            'https://www.ey.com/en_gl/technology'
        ]
    }
}


def bootstrap_site_graphs(registry: SiteGraphRegistry, 
                          discovery: RouteDiscovery) -> None:
    """
    Inizializza grafi per tutti i siti conosciuti
    Usa quick_scan per velocità
    """
    for site_name, config in KNOWN_SITE_ROUTES.items():
        if not registry.get_graph(site_name):
            graph = discovery.quick_scan(
                site_name=site_name,
                urls=config['entry_points']
            )
            registry.graphs[site_name] = graph
            registry.save_graph(site_name)
