# -*- coding: utf-8 -*-
"""
Topic Pipeline - Pipeline auto-aggiornante nodo→tema
Collega fonti ai loro temi, scarica report, analizza, e aggrega

Autore: Senior Python Developer
Data: 23 Dicembre 2025
"""

import json
import schedule
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from threading import Thread
import hashlib

from source_registry import SourceRegistry, SourceConfig, SourceStatus
from site_graph import SiteGraphRegistry, SiteGraph, NodeType
from route_discovery import RouteDiscovery
from document_manager import DocumentManager
from document_parser import DocumentParser
from ai_analyzer import AIAnalyzer, KeywordAnalyzer
from story_builder import StoryBuilder
import utils


@dataclass
class TopicData:
    """Dati aggregati per un singolo topic"""
    name: str
    sources: List[str] = field(default_factory=list)      # Fonti che coprono questo topic
    reports: List[Dict] = field(default_factory=list)     # Report recenti
    insights: List[Dict] = field(default_factory=list)    # Insights estratti
    narrative: str = ""                                    # Narrative aggregata
    last_updated: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'sources': self.sources,
            'reports': self.reports,
            'insights': self.insights,
            'narrative': self.narrative,
            'last_updated': self.last_updated
        }


class TopicPipeline:
    """
    Pipeline auto-aggiornante che:
    1. Scansiona fonti per nuovi report
    2. Scarica e analizza documenti
    3. Aggrega per topic
    4. Genera narrative
    """
    
    def __init__(self, 
                 storage_dir: str = None,
                 ai_provider: str = None,
                 ai_api_key: str = None):
        """
        Args:
            storage_dir: Directory per storage dati
            ai_provider: 'openai' o 'anthropic' (opzionale)
            ai_api_key: API key per AI
        """
        if storage_dir is None:
            storage_dir = Path(__file__).parent / 'data'
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Inizializza componenti
        self.source_registry = SourceRegistry(str(self.storage_dir / 'sources.json'))
        self.graph_registry = SiteGraphRegistry(str(self.storage_dir / 'graphs'))
        self.route_discovery = RouteDiscovery(max_depth=2, max_pages=50)
        self.document_manager = DocumentManager(str(self.storage_dir / 'documents'))
        self.document_parser = DocumentParser()
        
        # AI Analyzer (opzionale)
        if ai_provider and ai_api_key:
            try:
                self.ai_analyzer = AIAnalyzer(ai_provider, ai_api_key)
            except Exception as e:
                utils.logger.warning(f"⚠️ AI non disponibile: {e}")
                self.ai_analyzer = None
        else:
            self.ai_analyzer = None
        
        # Fallback keyword analyzer
        self.keyword_analyzer = KeywordAnalyzer()
        
        self.story_builder = StoryBuilder(self.ai_analyzer)
        
        # Topic data storage
        self.topics_data: Dict[str, TopicData] = {}
        self._load_topics_data()
        
        self.logger = utils.logger
        
        # State
        self.is_running = False
        self._scheduler_thread = None
    
    def _load_topics_data(self) -> None:
        """Carica dati topics esistenti"""
        topics_file = self.storage_dir / 'topics_data.json'
        
        if topics_file.exists():
            try:
                with open(topics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for topic_name, topic_data in data.items():
                    self.topics_data[topic_name] = TopicData(
                        name=topic_data['name'],
                        sources=topic_data.get('sources', []),
                        reports=topic_data.get('reports', []),
                        insights=topic_data.get('insights', []),
                        narrative=topic_data.get('narrative', ''),
                        last_updated=topic_data.get('last_updated', '')
                    )
                
                self.logger.info(f"📂 Caricati {len(self.topics_data)} topics")
            except Exception as e:
                self.logger.error(f"❌ Errore caricamento topics: {e}")
    
    def _save_topics_data(self) -> None:
        """Salva dati topics"""
        topics_file = self.storage_dir / 'topics_data.json'
        
        data = {name: td.to_dict() for name, td in self.topics_data.items()}
        
        with open(topics_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ==================== Core Pipeline Steps ====================
    
    def discover_sources(self, source_slugs: List[str] = None) -> None:
        """
        Step 1: Scopri struttura delle fonti
        
        Args:
            source_slugs: Lista di slug da scansionare (None = tutte le attive)
        """
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"📡 STEP 1: DISCOVERING SOURCES")
        self.logger.info(f"{'='*80}\n")
        
        if source_slugs is None:
            sources = self.source_registry.get_all_active()
            if not sources:
                sources = list(self.source_registry.sources.values())
        else:
            sources = [self.source_registry.get_source(s) for s in source_slugs]
            sources = [s for s in sources if s]
        
        for source in sources:
            self.logger.info(f"\n🔍 Scanning: {source.name}")
            
            try:
                # Quick scan degli entry points
                graph = self.route_discovery.quick_scan(
                    site_name=source.slug,
                    urls=source.entry_points
                )
                
                # Salva grafo
                self.graph_registry.graphs[source.slug] = graph
                self.graph_registry.save_graph(source.slug)
                
                # Aggiorna source
                source.last_scan = datetime.now().isoformat()
                source.report_count = len(graph.find_reports())
                source.mark_success()
                
                self.logger.info(f"  ✅ Trovati {source.report_count} report nodes")
            
            except Exception as e:
                source.mark_error(str(e))
                self.logger.error(f"  ❌ Errore: {e}")
        
        self.source_registry.save()
    
    def fetch_reports(self, topic: str = None, max_per_source: int = 5) -> List[Dict]:
        """
        Step 2: Scarica report dalle fonti
        
        Args:
            topic: Topic specifico (None = tutti)
            max_per_source: Max report per fonte
        
        Returns:
            Lista di report scaricati
        """
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"📥 STEP 2: FETCHING REPORTS")
        self.logger.info(f"   Topic filter: {topic or 'ALL'}")
        self.logger.info(f"{'='*80}\n")
        
        all_reports = []
        
        # Ottieni fonti per topic
        if topic:
            sources = self.source_registry.get_by_topic(topic)
        else:
            sources = self.source_registry.get_all_active()
        
        for source in sources:
            self.logger.info(f"\n📄 Fetching from: {source.name}")
            
            # Ottieni grafo del sito
            graph = self.graph_registry.get_graph(source.slug)
            
            if not graph:
                self.logger.warning(f"  ⚠️ Nessun grafo per {source.slug}")
                continue
            
            # Filtra report per topic se specificato
            if topic:
                report_nodes = graph.find_reports_by_topic(topic)
            else:
                report_nodes = graph.find_reports()
            
            # Limita
            report_nodes = report_nodes[:max_per_source]
            
            self.logger.info(f"  📊 {len(report_nodes)} report da scaricare")
            
            for node in report_nodes:
                report_info = {
                    'source': source.name,
                    'source_slug': source.slug,
                    'title': node.title,
                    'url': node.url,
                    'document_url': node.document_url,
                    'topics': node.topics,
                    'discovered_at': node.discovered_at
                }
                
                # Scarica documento se disponibile
                if node.document_url:
                    filepath = self.document_manager.download_document(report_info)
                    report_info['local_path'] = filepath
                
                all_reports.append(report_info)
        
        self.logger.info(f"\n✅ Totale report: {len(all_reports)}")
        
        return all_reports
    
    def analyze_reports(self, reports: List[Dict]) -> List[Dict]:
        """
        Step 3: Analizza report scaricati
        
        Args:
            reports: Lista di report da analizzare
        
        Returns:
            Lista di analisi
        """
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"🔬 STEP 3: ANALYZING REPORTS")
        self.logger.info(f"   Documents: {len(reports)}")
        self.logger.info(f"{'='*80}\n")
        
        analyses = []
        
        for report in reports:
            local_path = report.get('local_path')
            
            if not local_path:
                self.logger.warning(f"  ⚠️ No local file for: {report['title'][:50]}")
                continue
            
            self.logger.info(f"  📄 Analyzing: {report['title'][:60]}")
            
            # Parse documento
            parsed = self.document_parser.parse_document(local_path)
            
            if not parsed:
                continue
            
            # Analizza con AI o keywords
            if self.ai_analyzer:
                analysis = self.ai_analyzer.analyze_document(parsed)
            else:
                analysis = self.keyword_analyzer.analyze_document(parsed)
            
            if analysis:
                # Aggiungi metadata del report
                analysis['source'] = report['source']
                analysis['source_slug'] = report['source_slug']
                analysis['report_url'] = report['url']
                analysis['report_title'] = report['title']
                analysis['original_topics'] = report.get('topics', [])
                
                analyses.append(analysis)
        
        self.logger.info(f"\n✅ Analizzati: {len(analyses)} documenti")
        
        return analyses
    
    def aggregate_by_topic(self, analyses: List[Dict]) -> Dict[str, TopicData]:
        """
        Step 4: Aggrega analisi per topic
        
        Args:
            analyses: Lista di analisi
        
        Returns:
            Dict topic -> TopicData
        """
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"📊 STEP 4: AGGREGATING BY TOPIC")
        self.logger.info(f"{'='*80}\n")
        
        # Reset topic data (merge con esistenti)
        for analysis in analyses:
            # Get topics from analysis
            topics = analysis.get('topics', [])
            
            # Merge con original_topics
            topics = list(set(topics + analysis.get('original_topics', [])))
            
            for topic in topics:
                if topic not in self.topics_data:
                    self.topics_data[topic] = TopicData(name=topic)
                
                td = self.topics_data[topic]
                
                # Aggiungi source se non presente
                source_slug = analysis.get('source_slug', '')
                if source_slug and source_slug not in td.sources:
                    td.sources.append(source_slug)
                
                # Aggiungi report (evita duplicati per URL)
                report_url = analysis.get('report_url', '')
                existing_urls = [r.get('url') for r in td.reports]
                
                if report_url and report_url not in existing_urls:
                    td.reports.append({
                        'title': analysis.get('report_title', ''),
                        'url': report_url,
                        'source': analysis.get('source', ''),
                        'summary': analysis.get('summary', '')[:300],
                        'analyzed_at': analysis.get('analyzed_at', '')
                    })
                
                # Aggiungi insights
                for insight in analysis.get('key_insights', []):
                    td.insights.append({
                        'text': insight,
                        'source': analysis.get('source', ''),
                        'report': analysis.get('report_title', ''),
                        'confidence': analysis.get('confidence', 'medium')
                    })
                
                td.last_updated = datetime.now().isoformat()
        
        # Log risultati
        for topic, data in self.topics_data.items():
            self.logger.info(f"  📌 {topic}: {len(data.reports)} reports, {len(data.insights)} insights")
        
        self._save_topics_data()
        
        return self.topics_data
    
    def generate_narratives(self) -> None:
        """
        Step 5: Genera narrative per ogni topic
        """
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"📖 STEP 5: GENERATING NARRATIVES")
        self.logger.info(f"{'='*80}\n")
        
        for topic, data in self.topics_data.items():
            if not data.insights:
                continue
            
            self.logger.info(f"  📝 Generating narrative for: {topic}")
            
            # Prepara analisi per story builder
            fake_analyses = []
            for report in data.reports:
                fake_analyses.append({
                    'summary': report.get('summary', ''),
                    'key_insights': [i['text'] for i in data.insights if i.get('report') == report.get('title')],
                    'source_document': report.get('title', ''),
                    'confidence': 'medium'
                })
            
            if fake_analyses:
                story = self.story_builder._build_topic_story(topic, fake_analyses)
                data.narrative = story.get('narrative', '')
        
        self._save_topics_data()
        self.logger.info(f"\n✅ Narrative generate per {len(self.topics_data)} topics")
    
    # ==================== Full Pipeline ====================
    
    def run_full_pipeline(self, topics: List[str] = None) -> Dict[str, TopicData]:
        """
        Esegue pipeline completa
        
        Args:
            topics: Lista di topic da aggiornare (None = tutti)
        
        Returns:
            Topics data aggiornati
        """
        self.logger.info(f"\n{'#'*80}")
        self.logger.info(f"🚀 STARTING FULL PIPELINE")
        self.logger.info(f"   Topics: {topics or 'ALL'}")
        self.logger.info(f"   Time: {datetime.now().isoformat()}")
        self.logger.info(f"{'#'*80}\n")
        
        start_time = datetime.now()
        
        # Step 1: Discover
        self.discover_sources()
        
        # Step 2: Fetch
        if topics:
            all_reports = []
            for topic in topics:
                reports = self.fetch_reports(topic=topic)
                all_reports.extend(reports)
        else:
            all_reports = self.fetch_reports()
        
        # Step 3: Analyze
        analyses = self.analyze_reports(all_reports)
        
        # Step 4: Aggregate
        self.aggregate_by_topic(analyses)
        
        # Step 5: Narratives
        self.generate_narratives()
        
        elapsed = datetime.now() - start_time
        
        self.logger.info(f"\n{'#'*80}")
        self.logger.info(f"✅ PIPELINE COMPLETED")
        self.logger.info(f"   Elapsed: {elapsed}")
        self.logger.info(f"   Topics updated: {len(self.topics_data)}")
        self.logger.info(f"{'#'*80}\n")
        
        return self.topics_data
    
    # ==================== Scheduler ====================
    
    def start_scheduler(self, interval_hours: int = 24) -> None:
        """
        Avvia scheduler per aggiornamenti periodici
        
        Args:
            interval_hours: Intervallo tra aggiornamenti
        """
        self.is_running = True
        
        schedule.every(interval_hours).hours.do(self.run_full_pipeline)
        
        self.logger.info(f"⏰ Scheduler avviato: ogni {interval_hours} ore")
        
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)
        
        self._scheduler_thread = Thread(target=run_scheduler, daemon=True)
        self._scheduler_thread.start()
    
    def stop_scheduler(self) -> None:
        """Ferma scheduler"""
        self.is_running = False
        self.logger.info("⏹️ Scheduler fermato")
    
    # ==================== Getters ====================
    
    def get_topic_data(self, topic: str) -> Optional[TopicData]:
        """Ottiene dati per un topic"""
        return self.topics_data.get(topic)
    
    def get_all_topics(self) -> List[str]:
        """Lista di tutti i topics"""
        return list(self.topics_data.keys())
    
    def get_topic_summary(self) -> Dict:
        """Summary di tutti i topics"""
        return {
            'topics': [
                {
                    'name': td.name,
                    'sources': len(td.sources),
                    'reports': len(td.reports),
                    'insights': len(td.insights),
                    'has_narrative': bool(td.narrative),
                    'last_updated': td.last_updated
                }
                for td in self.topics_data.values()
            ],
            'total_topics': len(self.topics_data),
            'total_reports': sum(len(td.reports) for td in self.topics_data.values()),
            'total_insights': sum(len(td.insights) for td in self.topics_data.values())
        }
