# -*- coding: utf-8 -*-
"""
Global Insight Tracker v2.0
Sistema intelligente per aggregare insights per TOPIC da multiple fonti

Nuovo approccio:
1. Mappa siti come grafi navigabili
2. Auto-discovery delle rotte ai report
3. Pipeline nodo→tema auto-aggiornante
4. Dashboard per macro-tema con pensiero aggregato

Autore: Senior Python Developer
Data: 23 Dicembre 2025
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from source_registry import SourceRegistry, SourceType
from site_graph import SiteGraphRegistry
from route_discovery import RouteDiscovery, bootstrap_site_graphs
from topic_pipeline import TopicPipeline
from dashboard_generator import DashboardGenerator
import utils


def main():
    """Entry point principale"""
    
    parser = argparse.ArgumentParser(
        description='Global Insight Tracker v2.0 - Topic-based Intelligence Aggregation'
    )
    
    parser.add_argument(
        'command',
        choices=['discover', 'fetch', 'analyze', 'dashboard', 'full', 'status', 'sources'],
        help='Comando da eseguire'
    )
    
    parser.add_argument(
        '--topic', '-t',
        type=str,
        help='Topic specifico su cui operare (es: AI, Cloud, Cybersecurity)'
    )
    
    parser.add_argument(
        '--source', '-s',
        type=str,
        help='Fonte specifica su cui operare (es: deloitte, mckinsey)'
    )
    
    parser.add_argument(
        '--ai-provider',
        type=str,
        choices=['openai', 'anthropic'],
        help='Provider AI per analisi (richiede API key in env)'
    )
    
    parser.add_argument(
        '--max-reports',
        type=int,
        default=5,
        help='Max report per fonte'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Directory output'
    )
    
    args = parser.parse_args()
    
    # Setup
    logger = utils.logger
    
    logger.info(f"\n{'#'*80}")
    logger.info(f"🌍 GLOBAL INSIGHT TRACKER v2.0")
    logger.info(f"   Command: {args.command}")
    logger.info(f"   Time: {datetime.now().isoformat()}")
    logger.info(f"{'#'*80}\n")
    
    # Inizializza componenti
    base_dir = Path(__file__).parent
    data_dir = base_dir / 'data'
    output_dir = Path(args.output_dir) if args.output_dir else base_dir / 'output'
    
    # AI config
    ai_provider = args.ai_provider
    ai_api_key = None
    
    if ai_provider == 'openai':
        ai_api_key = os.getenv('OPENAI_API_KEY')
    elif ai_provider == 'anthropic':
        ai_api_key = os.getenv('ANTHROPIC_API_KEY')
    
    # Execute command
    if args.command == 'sources':
        # Mostra fonti disponibili
        registry = SourceRegistry(str(data_dir / 'sources.json'))
        census = registry.get_census()
        
        print("\n📊 SOURCE CENSUS")
        print("=" * 60)
        print(f"Total sources: {census['total_sources']}")
        print(f"Active: {census['active']}")
        print(f"Pending: {census['pending']}")
        print(f"Error: {census['error']}")
        print("\n📁 By Type:")
        for type_name, count in census['by_type'].items():
            if count > 0:
                print(f"  • {type_name}: {count}")
        print("\n🏷️ Topics Coverage:")
        for topic, count in list(census['topics'].items())[:10]:
            print(f"  • {topic}: {count} sources")
        print("\n📋 All Sources:")
        for source in census['sources']:
            status_icon = "✅" if source['status'] == 'active' else "⏳" if source['status'] == 'pending' else "❌"
            print(f"  {status_icon} {source['name']} ({source['slug']})")
            print(f"     Topics: {', '.join(source['topics'][:3])}")
    
    elif args.command == 'status':
        # Mostra stato pipeline
        pipeline = TopicPipeline(
            storage_dir=str(data_dir),
            ai_provider=ai_provider,
            ai_api_key=ai_api_key
        )
        
        summary = pipeline.get_topic_summary()
        
        print("\n📊 PIPELINE STATUS")
        print("=" * 60)
        print(f"Total Topics: {summary['total_topics']}")
        print(f"Total Reports: {summary['total_reports']}")
        print(f"Total Insights: {summary['total_insights']}")
        print("\n📌 Topics:")
        for topic in summary['topics']:
            narrative_icon = "📖" if topic['has_narrative'] else "  "
            print(f"  {narrative_icon} {topic['name']}")
            print(f"     Reports: {topic['reports']}, Insights: {topic['insights']}")
    
    elif args.command == 'discover':
        # Scopri struttura siti
        pipeline = TopicPipeline(
            storage_dir=str(data_dir),
            ai_provider=ai_provider,
            ai_api_key=ai_api_key
        )
        
        source_slugs = [args.source] if args.source else None
        pipeline.discover_sources(source_slugs)
        
        print("\n✅ Discovery completata!")
    
    elif args.command == 'fetch':
        # Scarica report
        pipeline = TopicPipeline(
            storage_dir=str(data_dir),
            ai_provider=ai_provider,
            ai_api_key=ai_api_key
        )
        
        reports = pipeline.fetch_reports(
            topic=args.topic,
            max_per_source=args.max_reports
        )
        
        print(f"\n✅ Scaricati {len(reports)} report")
    
    elif args.command == 'analyze':
        # Analizza report esistenti
        pipeline = TopicPipeline(
            storage_dir=str(data_dir),
            ai_provider=ai_provider,
            ai_api_key=ai_api_key
        )
        
        # Get existing documents
        doc_manager = pipeline.document_manager
        all_docs = doc_manager.get_all_documents()
        
        if args.topic:
            all_docs = doc_manager.get_documents_by_topic(args.topic)
        
        # Convert to report format
        reports = [
            {
                'source': d['source'],
                'source_slug': d['source'].lower().replace(' ', '_'),
                'title': d['title'],
                'url': d.get('report_url', ''),
                'local_path': d['filepath'],
                'topics': d.get('topics', [])
            }
            for d in all_docs
        ]
        
        analyses = pipeline.analyze_reports(reports)
        pipeline.aggregate_by_topic(analyses)
        pipeline.generate_narratives()
        
        print(f"\n✅ Analizzati {len(analyses)} documenti")
    
    elif args.command == 'dashboard':
        # Genera dashboard
        pipeline = TopicPipeline(
            storage_dir=str(data_dir),
            ai_provider=ai_provider,
            ai_api_key=ai_api_key
        )
        
        dashboard_gen = DashboardGenerator(str(output_dir))
        
        filepath = dashboard_gen.generate_dashboard(
            pipeline.topics_data,
            pipeline.source_registry
        )
        
        print(f"\n✅ Dashboard generata: {filepath}")
    
    elif args.command == 'full':
        # Pipeline completa
        topics = [args.topic] if args.topic else None
        
        pipeline = TopicPipeline(
            storage_dir=str(data_dir),
            ai_provider=ai_provider,
            ai_api_key=ai_api_key
        )
        
        # Run pipeline
        pipeline.run_full_pipeline(topics=topics)
        
        # Generate dashboard
        dashboard_gen = DashboardGenerator(str(output_dir))
        filepath = dashboard_gen.generate_dashboard(
            pipeline.topics_data,
            pipeline.source_registry
        )
        
        print(f"\n✅ Pipeline completata!")
        print(f"📊 Dashboard: {filepath}")


if __name__ == '__main__':
    main()
