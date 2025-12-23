#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Global Insight Tracker - CLI Entry Point
=========================================

Usage:
    python run.py [command] [options]
    
Commands:
    scrape      Esegue scraping delle fonti
    dashboard   Genera dashboard HTML
    stats       Mostra statistiche
    full        Pipeline completa: scrape → download → summarize → dashboard
    
Examples:
    python run.py scrape --sources deloitte mckinsey --max 10
    python run.py scrape --all --max 5
    python run.py dashboard
    python run.py stats
    python run.py full --sources deloitte mckinsey --max 5
"""

import argparse
import sys
import os
from datetime import datetime
from typing import List

# Carica variabili da .env
from dotenv import load_dotenv
load_dotenv()

# Aggiungi src al path
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.config import SOURCES, get_enabled_sources, OUTPUT_DIR, SCRAPING
from src.core.utils import logger, deduplicate_articles
from src.scrapers.selenium_scraper import SeleniumScraper
from src.analyzers.topic_classifier import TopicClassifier
from src.generators.excel_generator import ExcelGenerator
from src.generators.dashboard_generator import DashboardGenerator
from src.generators.story_builder import StoryBuilder
from src.generators.final_dashboard import FinalDashboard
from src.processors.document_downloader import DocumentDownloader
from src.processors.ai_summarizer import AISummarizer


def cmd_scrape(args):
    """Comando scrape"""
    print("\n" + "=" * 60)
    print("🚀 GLOBAL INSIGHT TRACKER - SCRAPING")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Determina fonti
    if args.all:
        sources = list(get_enabled_sources().keys())
    elif args.sources:
        sources = [s.lower() for s in args.sources if s.lower() in SOURCES]
    else:
        sources = ['deloitte', 'mckinsey', 'bcg']  # Default
    
    print(f"🎯 Fonti: {', '.join(s.upper() for s in sources)}")
    print(f"📊 Max articoli per fonte: {args.max}")
    print()
    
    # Scraping
    all_articles = []
    
    for source_key in sources:
        source = SOURCES.get(source_key)
        if not source:
            continue
        
        print(f"\n--- {source.name.upper()} ---")
        
        try:
            scraper = SeleniumScraper(source)
            articles = scraper.scrape(max_articles=args.max)
            all_articles.extend(articles)
            print(f"✅ {source.name}: {len(articles)} articoli")
        except Exception as e:
            print(f"❌ {source.name}: {e}")
    
    # Deduplica
    all_articles = deduplicate_articles(all_articles)
    
    # Classifica per topic
    classifier = TopicClassifier()
    all_articles = classifier.classify_all(all_articles)
    
    # Salva Excel
    print(f"\n💾 Salvataggio...")
    excel = ExcelGenerator()
    excel.save(all_articles)
    
    # Genera dashboard se richiesto
    if args.dashboard:
        topic_groups = classifier.group_by_topic(all_articles)
        dashboard = DashboardGenerator()
        dashboard.generate(all_articles, topic_groups)
    
    # Riepilogo
    print("\n" + "=" * 60)
    print("📊 RIEPILOGO")
    print("=" * 60)
    
    topic_stats = classifier.get_topic_stats(all_articles)
    for source_key in sources:
        count = sum(1 for a in all_articles if a.get('source', '').lower() == SOURCES[source_key].name.lower())
        status = "✅" if count > 0 else "⚠️"
        print(f"{status} {SOURCES[source_key].name}: {count} articoli")
    
    print("-" * 60)
    print(f"📈 TOTALE: {len(all_articles)} articoli")
    
    if topic_stats:
        print(f"\n📁 Top Topics:")
        for topic, count in sorted(topic_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   • {topic}: {count}")
    
    print("=" * 60)
    print(f"📄 Excel: {OUTPUT_DIR / 'report_consulting.xlsx'}")
    if args.dashboard:
        print(f"🌐 Dashboard: {OUTPUT_DIR / 'dashboard.html'}")
    
    return 0


def cmd_dashboard(args):
    """Comando dashboard"""
    print("\n🌐 Generazione Dashboard...")
    
    # Carica dati
    excel = ExcelGenerator()
    df = excel.load()
    
    if df.empty:
        print("❌ Nessun dato trovato. Esegui prima 'scrape'.")
        return 1
    
    articles = df.to_dict('records')
    
    # Classifica
    classifier = TopicClassifier()
    articles = classifier.classify_all(articles)
    topic_groups = classifier.group_by_topic(articles)
    
    # Genera
    dashboard = DashboardGenerator()
    dashboard.generate(articles, topic_groups)
    
    print(f"✅ Dashboard: {OUTPUT_DIR / 'dashboard.html'}")
    return 0


def cmd_stats(args):
    """Comando stats"""
    print("\n📊 STATISTICHE")
    print("=" * 60)
    
    excel = ExcelGenerator()
    stats = excel.get_stats()
    
    if stats['total'] == 0:
        print("Nessun dato. Esegui 'scrape' prima.")
        return 0
    
    print(f"📈 Totale articoli: {stats['total']}")
    
    print(f"\n📰 Per Fonte:")
    for src, count in sorted(stats['sources'].items(), key=lambda x: x[1], reverse=True):
        print(f"   • {src}: {count}")
    
    print(f"\n📁 Per Topic:")
    for topic, count in sorted(stats['topics'].items(), key=lambda x: x[1], reverse=True):
        print(f"   • {topic}: {count}")
    
    return 0


def cmd_full(args):
    """
    Pipeline completa:
    1. Scrape articoli
    2. Download contenuti (PDF/HTML)
    3. Riassumi con AI (OpenAI)
    4. Genera dashboard finale con recap per topic
    """
    print("\n" + "=" * 70)
    print("🚀 GLOBAL INSIGHT TRACKER - PIPELINE COMPLETA")
    print("=" * 70)
    print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # ===== 1. SCRAPING =====
    print("\n📡 FASE 1: SCRAPING")
    print("-" * 40)
    
    if args.all:
        sources = list(get_enabled_sources().keys())
    elif args.sources:
        sources = [s.lower() for s in args.sources if s.lower() in SOURCES]
    else:
        sources = ['deloitte', 'mckinsey', 'bcg']
    
    print(f"🎯 Fonti: {', '.join(s.upper() for s in sources)}")
    print(f"📊 Max articoli per fonte: {args.max}")
    
    all_articles = []
    
    for source_key in sources:
        source = SOURCES.get(source_key)
        if not source:
            continue
        
        try:
            scraper = SeleniumScraper(source)
            articles = scraper.scrape(max_articles=args.max)
            all_articles.extend(articles)
            print(f"   ✅ {source.name}: {len(articles)} articoli")
        except Exception as e:
            print(f"   ❌ {source.name}: {e}")
    
    all_articles = deduplicate_articles(all_articles)
    print(f"\n📈 Totale articoli: {len(all_articles)}")
    
    # Classifica per topic
    classifier = TopicClassifier()
    all_articles = classifier.classify_all(all_articles)
    
    # ===== 2. DOWNLOAD CONTENUTI =====
    print("\n📥 FASE 2: DOWNLOAD CONTENUTI")
    print("-" * 40)
    
    if args.skip_download:
        print("⏭️ Skip download (--skip-download)")
    else:
        downloader = DocumentDownloader()
        all_articles = downloader.download_all(all_articles)
        
        with_content = sum(1 for a in all_articles if a.get('content'))
        print(f"✅ Contenuti scaricati: {with_content}/{len(all_articles)}")
    
    # ===== 3. RIASSUNTI AI =====
    print("\n🤖 FASE 3: RIASSUNTI AI")
    print("-" * 40)
    
    import os
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("⚠️ OPENAI_API_KEY non trovata!")
        print("   Per abilitare i riassunti AI:")
        print("   set OPENAI_API_KEY=sk-your-key-here")
        print("   oppure crea file .env con OPENAI_API_KEY=sk-your-key-here")
        print("\n   Continuo senza riassunti AI...")
    elif args.skip_summary:
        print("⏭️ Skip riassunti (--skip-summary)")
    else:
        try:
            summarizer = AISummarizer()
            all_articles = summarizer.summarize_all(all_articles, max_summaries=args.summary_per_topic * 10)
            
            with_summary = sum(1 for a in all_articles if a.get('summary'))
            print(f"✅ Articoli con riassunto: {with_summary}/{len(all_articles)}")
        except Exception as e:
            print(f"❌ Errore AI: {e}")
    
    # ===== 4. GENERA DASHBOARD =====
    print("\n🌐 FASE 4: GENERAZIONE DASHBOARD")
    print("-" * 40)
    
    topic_groups = classifier.group_by_topic(all_articles)
    
    # Genera recap per topic se abbiamo API key
    topic_recaps = {}
    if api_key and not args.skip_summary:
        try:
            summarizer = AISummarizer()
            topic_recaps = summarizer.generate_all_recaps(topic_groups)
            print(f"✅ Recap generati per {len(topic_recaps)} topics")
        except Exception as e:
            print(f"⚠️ Recap non generati: {e}")
    
    # Dashboard finale
    dashboard = FinalDashboard()
    success = dashboard.generate(all_articles, topic_groups, topic_recaps)
    
    if success:
        print(f"✅ Dashboard: {OUTPUT_DIR / 'final_dashboard.html'}")
        print(f"✅ JSON: {OUTPUT_DIR / 'insights_data.json'}")
    
    # Salva anche Excel
    excel = ExcelGenerator()
    excel.save(all_articles)
    print(f"✅ Excel: {OUTPUT_DIR / 'report_consulting.xlsx'}")
    
    # ===== RIEPILOGO =====
    print("\n" + "=" * 70)
    print("📊 RIEPILOGO PIPELINE")
    print("=" * 70)
    
    print(f"\n📈 Articoli totali: {len(all_articles)}")
    with_content = sum(1 for a in all_articles if a.get('content'))
    with_summary = sum(1 for a in all_articles if a.get('summary'))
    print(f"📄 Con contenuto: {with_content}")
    print(f"📝 Con riassunto: {with_summary}")
    print(f"📁 Topics: {len(topic_groups)}")
    print(f"💡 Topic recaps: {len(topic_recaps)}")
    
    print(f"\n📰 Per Fonte:")
    for source_key in sources:
        source_name = SOURCES[source_key].name
        count = sum(1 for a in all_articles if a.get('source', '').lower() == source_name.lower())
        print(f"   • {source_name}: {count}")
    
    print(f"\n📁 Top Topics:")
    topic_stats = classifier.get_topic_stats(all_articles)
    for topic, count in sorted(topic_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   • {topic}: {count}")
    
    print("\n" + "=" * 70)
    print("🎉 Pipeline completata!")
    print(f"🌐 Apri: {OUTPUT_DIR / 'final_dashboard.html'}")
    print("=" * 70)
    
    return 0


def main():
    """Entry point principale"""
    parser = argparse.ArgumentParser(
        description='Global Insight Tracker - Monitor tecnologie dirompenti',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandi disponibili')
    
    # Comando scrape
    scrape_parser = subparsers.add_parser('scrape', help='Esegue scraping')
    scrape_parser.add_argument(
        '--sources', '-s', 
        nargs='+',
        choices=list(SOURCES.keys()),
        help='Fonti da scrapare'
    )
    scrape_parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Scrape tutte le fonti'
    )
    scrape_parser.add_argument(
        '--max', '-m',
        type=int,
        default=10,
        help='Max articoli per fonte (default: 10)'
    )
    scrape_parser.add_argument(
        '--dashboard', '-d',
        action='store_true',
        help='Genera anche dashboard'
    )
    
    # Comando dashboard
    dash_parser = subparsers.add_parser('dashboard', help='Genera dashboard HTML')
    
    # Comando stats
    stats_parser = subparsers.add_parser('stats', help='Mostra statistiche')
    
    # Comando full (pipeline completa)
    full_parser = subparsers.add_parser('full', help='Pipeline completa: scrape → download → summarize → dashboard')
    full_parser.add_argument(
        '--sources', '-s', 
        nargs='+',
        choices=list(SOURCES.keys()),
        help='Fonti da processare'
    )
    full_parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Processa tutte le fonti'
    )
    full_parser.add_argument(
        '--max', '-m',
        type=int,
        default=5,
        help='Max articoli per fonte (default: 5)'
    )
    full_parser.add_argument(
        '--skip-download',
        action='store_true',
        help='Salta download contenuti'
    )
    full_parser.add_argument(
        '--skip-summary',
        action='store_true',
        help='Salta riassunti AI'
    )
    full_parser.add_argument(
        '--summary-per-topic',
        type=int,
        default=3,
        help='Max articoli da riassumere per topic (default: 3)'
    )
    
    # Parse
    args = parser.parse_args()
    
    if args.command == 'scrape':
        return cmd_scrape(args)
    elif args.command == 'dashboard':
        return cmd_dashboard(args)
    elif args.command == 'stats':
        return cmd_stats(args)
    elif args.command == 'full':
        return cmd_full(args)
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrotto dall'utente")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Errore: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
