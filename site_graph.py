# -*- coding: utf-8 -*-
"""
Site Graph - Rappresentazione di siti web come grafi navigabili
Ogni sito è un grafo di nodi (pagine) con edges (link) da navigare per raggiungere i report

Autore: Senior Python Developer
Data: 23 Dicembre 2025
"""

import json
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set
from datetime import datetime
from pathlib import Path
from enum import Enum
from collections import deque

import utils


class NodeType(Enum):
    """Tipo di nodo nel grafo del sito"""
    HOME = "home"                   # Homepage del sito
    SECTION = "section"             # Sezione (es. /insights, /research)
    LISTING = "listing"             # Pagina con lista di report
    REPORT_PAGE = "report_page"     # Pagina singola di un report
    DOCUMENT = "document"           # Link diretto a documento (PDF, DOCX)
    UNKNOWN = "unknown"             # Ancora da classificare


@dataclass
class GraphNode:
    """Singolo nodo nel grafo del sito"""
    url: str
    node_type: NodeType = NodeType.UNKNOWN
    title: str = ""
    topics: List[str] = field(default_factory=list)
    
    # Navigazione
    depth: int = 0                  # Distanza dalla homepage
    parent_url: Optional[str] = None
    
    # Stato
    discovered_at: str = ""
    last_visited: str = ""
    visit_count: int = 0
    is_active: bool = True          # Se il link è ancora valido
    
    # Per report/documenti
    document_url: Optional[str] = None  # URL del PDF/DOCX se trovato
    
    # Metadata estratti
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.discovered_at:
            self.discovered_at = datetime.now().isoformat()
    
    @property
    def node_id(self) -> str:
        """ID univoco basato su hash URL"""
        return hashlib.md5(self.url.encode()).hexdigest()[:12]
    
    def to_dict(self) -> Dict:
        """Converte in dizionario serializzabile"""
        d = asdict(self)
        d['node_type'] = self.node_type.value
        return d
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GraphNode':
        """Crea da dizionario"""
        data = data.copy()
        data['node_type'] = NodeType(data['node_type'])
        return cls(**data)


@dataclass
class GraphEdge:
    """Connessione tra due nodi"""
    from_url: str
    to_url: str
    link_text: str = ""             # Testo del link
    edge_type: str = "navigation"   # navigation, download, related
    weight: float = 1.0             # Importanza (1.0 = normale)
    
    def to_dict(self) -> Dict:
        return asdict(self)


class SiteGraph:
    """
    Rappresentazione di un sito web come grafo navigabile.
    Permette di:
    - Mappare la struttura del sito
    - Trovare rotte ottimali ai report
    - Salvare/caricare la mappa per riutilizzo
    """
    
    def __init__(self, site_name: str, base_url: str):
        self.site_name = site_name
        self.base_url = base_url.rstrip('/')
        
        self.nodes: Dict[str, GraphNode] = {}      # url -> node
        self.edges: List[GraphEdge] = []
        self.adjacency: Dict[str, Set[str]] = {}   # url -> set di url collegati
        
        # Rotte conosciute verso tipi di contenuto
        self.known_routes: Dict[str, List[str]] = {
            'reports': [],      # URL che portano a listing di report
            'insights': [],     # URL di insights
            'documents': [],    # URL diretti a documenti
        }
        
        # Topics coperti da questo sito
        self.site_topics: Set[str] = set()
        
        # Metadata
        self.created_at = datetime.now().isoformat()
        self.last_updated = self.created_at
        
        self.logger = utils.logger
    
    def add_node(self, node: GraphNode) -> None:
        """Aggiunge un nodo al grafo"""
        self.nodes[node.url] = node
        
        if node.url not in self.adjacency:
            self.adjacency[node.url] = set()
        
        # Aggiorna topics del sito
        self.site_topics.update(node.topics)
        
        self.last_updated = datetime.now().isoformat()
    
    def add_edge(self, from_url: str, to_url: str, 
                 link_text: str = "", edge_type: str = "navigation") -> None:
        """Aggiunge connessione tra due nodi"""
        
        edge = GraphEdge(
            from_url=from_url,
            to_url=to_url,
            link_text=link_text,
            edge_type=edge_type
        )
        
        self.edges.append(edge)
        
        # Aggiorna adjacency list
        if from_url not in self.adjacency:
            self.adjacency[from_url] = set()
        self.adjacency[from_url].add(to_url)
    
    def get_node(self, url: str) -> Optional[GraphNode]:
        """Ottiene nodo per URL"""
        return self.nodes.get(url)
    
    def find_path(self, from_url: str, to_url: str) -> List[str]:
        """
        Trova percorso più breve tra due URL usando BFS
        
        Returns:
            Lista di URL che compongono il percorso, o lista vuota se non trovato
        """
        if from_url not in self.nodes or to_url not in self.nodes:
            return []
        
        if from_url == to_url:
            return [from_url]
        
        # BFS
        queue = deque([(from_url, [from_url])])
        visited = {from_url}
        
        while queue:
            current, path = queue.popleft()
            
            for neighbor in self.adjacency.get(current, []):
                if neighbor == to_url:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []
    
    def find_reports(self) -> List[GraphNode]:
        """Trova tutti i nodi che sono report"""
        return [
            node for node in self.nodes.values()
            if node.node_type in [NodeType.REPORT_PAGE, NodeType.DOCUMENT]
        ]
    
    def find_reports_by_topic(self, topic: str) -> List[GraphNode]:
        """Trova report per un dato topic"""
        return [
            node for node in self.nodes.values()
            if node.node_type in [NodeType.REPORT_PAGE, NodeType.DOCUMENT]
            and topic in node.topics
        ]
    
    def get_route_to_reports(self) -> Dict[str, List[str]]:
        """
        Ottiene le rotte migliori dalla homepage ai report
        
        Returns:
            Dict topic -> lista URL del percorso
        """
        routes = {}
        homepage = self.base_url
        
        # Se homepage non nel grafo, usa primo nodo
        if homepage not in self.nodes:
            if self.nodes:
                homepage = list(self.nodes.keys())[0]
            else:
                return {}
        
        # Per ogni report, trova la rotta
        for node in self.find_reports():
            path = self.find_path(homepage, node.url)
            
            if path:
                for topic in node.topics:
                    if topic not in routes or len(path) < len(routes[topic]):
                        routes[topic] = path
        
        return routes
    
    def register_report_route(self, route_type: str, url: str) -> None:
        """Registra una rotta conosciuta"""
        if route_type in self.known_routes:
            if url not in self.known_routes[route_type]:
                self.known_routes[route_type].append(url)
    
    def get_stats(self) -> Dict:
        """Statistiche del grafo"""
        node_types = {}
        for node in self.nodes.values():
            t = node.node_type.value
            node_types[t] = node_types.get(t, 0) + 1
        
        return {
            'site_name': self.site_name,
            'base_url': self.base_url,
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'node_types': node_types,
            'topics_covered': list(self.site_topics),
            'known_report_routes': len(self.known_routes.get('reports', [])),
            'created_at': self.created_at,
            'last_updated': self.last_updated
        }
    
    def save(self, filepath: str) -> None:
        """Salva grafo su file JSON"""
        data = {
            'site_name': self.site_name,
            'base_url': self.base_url,
            'nodes': {url: node.to_dict() for url, node in self.nodes.items()},
            'edges': [e.to_dict() for e in self.edges],
            'known_routes': self.known_routes,
            'site_topics': list(self.site_topics),
            'created_at': self.created_at,
            'last_updated': self.last_updated
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 Grafo salvato: {filepath}")
    
    @classmethod
    def load(cls, filepath: str) -> 'SiteGraph':
        """Carica grafo da file JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        graph = cls(data['site_name'], data['base_url'])
        
        # Ricostruisci nodi
        for url, node_data in data['nodes'].items():
            graph.nodes[url] = GraphNode.from_dict(node_data)
        
        # Ricostruisci edges
        for edge_data in data['edges']:
            graph.edges.append(GraphEdge(**edge_data))
            
            from_url = edge_data['from_url']
            to_url = edge_data['to_url']
            
            if from_url not in graph.adjacency:
                graph.adjacency[from_url] = set()
            graph.adjacency[from_url].add(to_url)
        
        graph.known_routes = data.get('known_routes', {})
        graph.site_topics = set(data.get('site_topics', []))
        graph.created_at = data.get('created_at', '')
        graph.last_updated = data.get('last_updated', '')
        
        return graph
    
    def __repr__(self):
        return f"SiteGraph({self.site_name}, nodes={len(self.nodes)}, edges={len(self.edges)})"


class SiteGraphRegistry:
    """
    Registro di tutti i grafi dei siti.
    Gestisce il censimento delle fonti e le loro mappe.
    """
    
    def __init__(self, storage_dir: str = None):
        if storage_dir is None:
            storage_dir = Path(__file__).parent / 'data' / 'graphs'
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.graphs: Dict[str, SiteGraph] = {}
        self.logger = utils.logger
        
        # Carica grafi esistenti
        self._load_all_graphs()
    
    def _load_all_graphs(self) -> None:
        """Carica tutti i grafi salvati"""
        for filepath in self.storage_dir.glob('*.json'):
            try:
                graph = SiteGraph.load(str(filepath))
                self.graphs[graph.site_name.lower()] = graph
                self.logger.info(f"📂 Caricato grafo: {graph.site_name}")
            except Exception as e:
                self.logger.error(f"❌ Errore caricamento {filepath}: {e}")
    
    def register_site(self, site_name: str, base_url: str) -> SiteGraph:
        """Registra nuovo sito o ritorna esistente"""
        key = site_name.lower()
        
        if key in self.graphs:
            return self.graphs[key]
        
        graph = SiteGraph(site_name, base_url)
        self.graphs[key] = graph
        
        # Salva immediatamente
        self.save_graph(key)
        
        self.logger.info(f"✅ Registrato nuovo sito: {site_name}")
        
        return graph
    
    def get_graph(self, site_name: str) -> Optional[SiteGraph]:
        """Ottiene grafo per nome sito"""
        return self.graphs.get(site_name.lower())
    
    def save_graph(self, site_name: str) -> None:
        """Salva grafo specifico"""
        key = site_name.lower()
        
        if key in self.graphs:
            filepath = self.storage_dir / f"{key}.json"
            self.graphs[key].save(str(filepath))
    
    def save_all(self) -> None:
        """Salva tutti i grafi"""
        for key in self.graphs:
            self.save_graph(key)
    
    def get_all_topics(self) -> Dict[str, List[str]]:
        """
        Ottiene mappa topic -> siti che lo coprono
        
        Returns:
            Dict con topic come key e lista siti come value
        """
        topic_sites = {}
        
        for site_name, graph in self.graphs.items():
            for topic in graph.site_topics:
                if topic not in topic_sites:
                    topic_sites[topic] = []
                topic_sites[topic].append(site_name)
        
        return topic_sites
    
    def find_sources_for_topic(self, topic: str) -> List[SiteGraph]:
        """Trova tutti i siti che coprono un topic"""
        return [
            graph for graph in self.graphs.values()
            if topic in graph.site_topics
        ]
    
    def get_census(self) -> Dict:
        """
        Ritorna censimento completo di tutte le fonti
        """
        census = {
            'total_sites': len(self.graphs),
            'sites': {},
            'topics_coverage': self.get_all_topics(),
            'generated_at': datetime.now().isoformat()
        }
        
        for site_name, graph in self.graphs.items():
            census['sites'][site_name] = graph.get_stats()
        
        return census
