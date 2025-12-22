# -*- coding: utf-8 -*-
"""
Source Registry - Censimento completo delle fonti
Database di tutte le fonti con metadata, temi, stato, e configurazione

Autore: Senior Python Developer
Data: 23 Dicembre 2025
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set
from datetime import datetime
from pathlib import Path
from enum import Enum

import utils


class SourceStatus(Enum):
    """Stato di una fonte"""
    ACTIVE = "active"           # Fonte attiva e funzionante
    PENDING = "pending"         # Da configurare
    ERROR = "error"             # Errori nel fetching
    DISABLED = "disabled"       # Disabilitata manualmente


class SourceType(Enum):
    """Tipo di fonte"""
    CONSULTING = "consulting"           # Big 4, MBB
    RESEARCH = "research"               # Gartner, Forrester
    TECH_COMPANY = "tech_company"       # Google, Microsoft, AWS
    THINK_TANK = "think_tank"           # WEF, Brookings
    GOVERNMENT = "government"           # Enti governativi
    ACADEMIC = "academic"               # Università, centri ricerca
    NEWS = "news"                       # Tech news


@dataclass
class SourceConfig:
    """Configurazione di una singola fonte"""
    
    # Identificazione
    name: str
    slug: str                           # Identificatore univoco (es. "deloitte")
    source_type: SourceType
    
    # URLs
    base_url: str
    entry_points: List[str] = field(default_factory=list)
    
    # Topics coperti da questa fonte
    topics: List[str] = field(default_factory=list)
    primary_topics: List[str] = field(default_factory=list)  # Topics principali
    
    # Stato
    status: SourceStatus = SourceStatus.PENDING
    last_scan: Optional[str] = None
    last_successful_fetch: Optional[str] = None
    error_count: int = 0
    last_error: Optional[str] = None
    
    # Configurazione scraping
    requires_javascript: bool = False   # Se serve Selenium/Playwright
    rate_limit: float = 2.0             # Secondi tra richieste
    max_depth: int = 3                  # Profondità navigazione
    
    # Quality metrics
    report_count: int = 0               # Report trovati
    last_report_date: Optional[str] = None
    reliability_score: float = 1.0      # 0-1, quanto è affidabile
    
    # Metadata
    description: str = ""
    logo_url: str = ""
    region: str = "global"              # global, us, eu, etc.
    
    # Timestamp
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['source_type'] = self.source_type.value
        d['status'] = self.status.value
        return d
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SourceConfig':
        data = data.copy()
        data['source_type'] = SourceType(data['source_type'])
        data['status'] = SourceStatus(data['status'])
        return cls(**data)
    
    def mark_success(self) -> None:
        """Segna fetch riuscito"""
        self.last_successful_fetch = datetime.now().isoformat()
        self.error_count = 0
        self.last_error = None
        self.status = SourceStatus.ACTIVE
        self.updated_at = datetime.now().isoformat()
    
    def mark_error(self, error: str) -> None:
        """Segna errore"""
        self.error_count += 1
        self.last_error = error
        self.updated_at = datetime.now().isoformat()
        
        if self.error_count >= 5:
            self.status = SourceStatus.ERROR


class SourceRegistry:
    """
    Registro centrale di tutte le fonti.
    Gestisce censimento, configurazione, e stato.
    """
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = Path(__file__).parent / 'data' / 'sources.json'
        
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.sources: Dict[str, SourceConfig] = {}
        self.logger = utils.logger
        
        # Carica fonti esistenti o inizializza defaults
        if self.storage_path.exists():
            self._load()
        else:
            self._initialize_defaults()
    
    def _load(self) -> None:
        """Carica registry da file"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for slug, source_data in data.get('sources', {}).items():
                self.sources[slug] = SourceConfig.from_dict(source_data)
            
            self.logger.info(f"📂 Caricato registry: {len(self.sources)} fonti")
        except Exception as e:
            self.logger.error(f"❌ Errore caricamento registry: {e}")
            self._initialize_defaults()
    
    def save(self) -> None:
        """Salva registry su file"""
        data = {
            'version': '2.0',
            'updated_at': datetime.now().isoformat(),
            'sources': {slug: s.to_dict() for slug, s in self.sources.items()}
        }
        
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 Registry salvato: {len(self.sources)} fonti")
    
    def _initialize_defaults(self) -> None:
        """Inizializza fonti di default"""
        
        default_sources = [
            # Big 4
            SourceConfig(
                name="Deloitte",
                slug="deloitte",
                source_type=SourceType.CONSULTING,
                base_url="https://www2.deloitte.com",
                entry_points=[
                    "https://www2.deloitte.com/us/en/insights.html",
                    "https://www2.deloitte.com/us/en/insights/focus/tech-trends.html",
                    "https://www2.deloitte.com/us/en/insights/topics/digital-transformation.html"
                ],
                topics=["AI", "Cloud", "Cybersecurity", "Digital Transformation", "Data"],
                primary_topics=["AI", "Digital Transformation"],
                description="Global consulting firm with Tech Trends annual report"
            ),
            SourceConfig(
                name="PwC",
                slug="pwc",
                source_type=SourceType.CONSULTING,
                base_url="https://www.pwc.com",
                entry_points=[
                    "https://www.pwc.com/gx/en/issues.html",
                    "https://www.pwc.com/gx/en/issues/technology.html"
                ],
                topics=["AI", "ESG", "Digital Transformation", "Cybersecurity"],
                primary_topics=["AI", "ESG"],
                description="Big 4 firm with CEO Survey and Global Digital Trust"
            ),
            SourceConfig(
                name="KPMG",
                slug="kpmg",
                source_type=SourceType.CONSULTING,
                base_url="https://kpmg.com",
                entry_points=[
                    "https://kpmg.com/xx/en/home/insights.html"
                ],
                topics=["AI", "ESG", "Cloud", "Digital Transformation"],
                primary_topics=["Digital Transformation"],
                description="Big 4 consulting with global insights"
            ),
            SourceConfig(
                name="EY",
                slug="ey",
                source_type=SourceType.CONSULTING,
                base_url="https://www.ey.com",
                entry_points=[
                    "https://www.ey.com/en_gl/insights"
                ],
                topics=["AI", "ESG", "Digital Transformation"],
                primary_topics=["ESG"],
                description="Big 4 firm focused on sustainability"
            ),
            
            # MBB
            SourceConfig(
                name="McKinsey",
                slug="mckinsey",
                source_type=SourceType.CONSULTING,
                base_url="https://www.mckinsey.com",
                entry_points=[
                    "https://www.mckinsey.com/featured-insights",
                    "https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights"
                ],
                topics=["AI", "Digital Transformation", "Data", "Automation"],
                primary_topics=["AI", "Digital Transformation"],
                description="Top strategy consulting with MGI research"
            ),
            SourceConfig(
                name="BCG",
                slug="bcg",
                source_type=SourceType.CONSULTING,
                base_url="https://www.bcg.com",
                entry_points=[
                    "https://www.bcg.com/publications"
                ],
                topics=["AI", "Digital Transformation", "ESG", "Innovation"],
                primary_topics=["AI", "Innovation"],
                description="Strategy consulting with Henderson Institute"
            ),
            SourceConfig(
                name="Bain",
                slug="bain",
                source_type=SourceType.CONSULTING,
                base_url="https://www.bain.com",
                entry_points=[
                    "https://www.bain.com/insights/"
                ],
                topics=["AI", "Digital Transformation", "Private Equity"],
                primary_topics=["Digital Transformation"],
                description="Strategy consulting with sector expertise"
            ),
            
            # Tech Advisory
            SourceConfig(
                name="Accenture",
                slug="accenture",
                source_type=SourceType.CONSULTING,
                base_url="https://www.accenture.com",
                entry_points=[
                    "https://www.accenture.com/us-en/insights"
                ],
                topics=["AI", "Cloud", "Digital Transformation", "Metaverse"],
                primary_topics=["AI", "Cloud"],
                description="Tech consulting with Technology Vision report"
            ),
            
            # Research Firms
            SourceConfig(
                name="Gartner",
                slug="gartner",
                source_type=SourceType.RESEARCH,
                base_url="https://www.gartner.com",
                entry_points=[
                    "https://www.gartner.com/en/articles",
                    "https://www.gartner.com/en/information-technology/insights"
                ],
                topics=["AI", "Cloud", "Cybersecurity", "Data", "IoT"],
                primary_topics=["AI", "Cloud"],
                description="IT research with Hype Cycle and Magic Quadrant",
                requires_javascript=True
            ),
            SourceConfig(
                name="Forrester",
                slug="forrester",
                source_type=SourceType.RESEARCH,
                base_url="https://www.forrester.com",
                entry_points=[
                    "https://www.forrester.com/research/"
                ],
                topics=["AI", "CX", "Digital Transformation", "Cloud"],
                primary_topics=["CX", "AI"],
                description="Technology and market research",
                requires_javascript=True
            ),
            
            # Think Tanks
            SourceConfig(
                name="World Economic Forum",
                slug="wef",
                source_type=SourceType.THINK_TANK,
                base_url="https://www.weforum.org",
                entry_points=[
                    "https://www.weforum.org/publications/"
                ],
                topics=["AI", "ESG", "Future of Work", "Geopolitics"],
                primary_topics=["AI", "ESG"],
                description="Global issues and technology governance"
            ),
            SourceConfig(
                name="Brookings",
                slug="brookings",
                source_type=SourceType.THINK_TANK,
                base_url="https://www.brookings.edu",
                entry_points=[
                    "https://www.brookings.edu/topic/technology-innovation/"
                ],
                topics=["AI", "Policy", "Digital Transformation"],
                primary_topics=["AI", "Policy"],
                description="Policy research on technology"
            ),
            
            # Tech Companies
            SourceConfig(
                name="Google AI",
                slug="google_ai",
                source_type=SourceType.TECH_COMPANY,
                base_url="https://ai.google",
                entry_points=[
                    "https://ai.google/research/",
                    "https://blog.google/technology/ai/"
                ],
                topics=["AI", "Machine Learning", "Quantum"],
                primary_topics=["AI"],
                description="Google AI research and blog"
            ),
            SourceConfig(
                name="Microsoft Research",
                slug="microsoft_research",
                source_type=SourceType.TECH_COMPANY,
                base_url="https://www.microsoft.com",
                entry_points=[
                    "https://www.microsoft.com/en-us/research/"
                ],
                topics=["AI", "Cloud", "Quantum", "Security"],
                primary_topics=["AI", "Cloud"],
                description="Microsoft research publications"
            ),
            SourceConfig(
                name="AWS",
                slug="aws",
                source_type=SourceType.TECH_COMPANY,
                base_url="https://aws.amazon.com",
                entry_points=[
                    "https://aws.amazon.com/blogs/",
                    "https://aws.amazon.com/executive-insights/"
                ],
                topics=["Cloud", "AI", "Data", "Security"],
                primary_topics=["Cloud"],
                description="AWS whitepapers and blogs"
            )
        ]
        
        for source in default_sources:
            self.sources[source.slug] = source
        
        self.save()
        self.logger.info(f"✅ Inizializzato registry con {len(self.sources)} fonti default")
    
    # ==================== CRUD Operations ====================
    
    def add_source(self, source: SourceConfig) -> None:
        """Aggiunge nuova fonte"""
        self.sources[source.slug] = source
        self.save()
        self.logger.info(f"✅ Fonte aggiunta: {source.name}")
    
    def get_source(self, slug: str) -> Optional[SourceConfig]:
        """Ottiene fonte per slug"""
        return self.sources.get(slug)
    
    def remove_source(self, slug: str) -> bool:
        """Rimuove fonte"""
        if slug in self.sources:
            del self.sources[slug]
            self.save()
            return True
        return False
    
    def update_source(self, slug: str, **kwargs) -> bool:
        """Aggiorna campi di una fonte"""
        if slug in self.sources:
            source = self.sources[slug]
            for key, value in kwargs.items():
                if hasattr(source, key):
                    setattr(source, key, value)
            source.updated_at = datetime.now().isoformat()
            self.save()
            return True
        return False
    
    # ==================== Query Methods ====================
    
    def get_all_active(self) -> List[SourceConfig]:
        """Ottiene tutte le fonti attive"""
        return [s for s in self.sources.values() if s.status == SourceStatus.ACTIVE]
    
    def get_by_topic(self, topic: str) -> List[SourceConfig]:
        """Ottiene fonti che coprono un topic"""
        return [s for s in self.sources.values() if topic in s.topics]
    
    def get_by_type(self, source_type: SourceType) -> List[SourceConfig]:
        """Ottiene fonti per tipo"""
        return [s for s in self.sources.values() if s.source_type == source_type]
    
    def get_primary_sources_for_topic(self, topic: str) -> List[SourceConfig]:
        """Ottiene fonti dove topic è primario"""
        return [s for s in self.sources.values() if topic in s.primary_topics]
    
    def get_all_topics(self) -> Dict[str, int]:
        """Ottiene tutti i topics con count fonti"""
        topic_counts = {}
        for source in self.sources.values():
            for topic in source.topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        return dict(sorted(topic_counts.items(), key=lambda x: -x[1]))
    
    def get_census(self) -> Dict:
        """Ottiene censimento completo"""
        return {
            'total_sources': len(self.sources),
            'active': len([s for s in self.sources.values() if s.status == SourceStatus.ACTIVE]),
            'pending': len([s for s in self.sources.values() if s.status == SourceStatus.PENDING]),
            'error': len([s for s in self.sources.values() if s.status == SourceStatus.ERROR]),
            'by_type': {
                t.value: len([s for s in self.sources.values() if s.source_type == t])
                for t in SourceType
            },
            'topics': self.get_all_topics(),
            'sources': [
                {
                    'name': s.name,
                    'slug': s.slug,
                    'type': s.source_type.value,
                    'status': s.status.value,
                    'topics': s.topics,
                    'report_count': s.report_count
                }
                for s in self.sources.values()
            ]
        }
