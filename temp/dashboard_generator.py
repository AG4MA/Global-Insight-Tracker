# -*- coding: utf-8 -*-
"""
Dashboard Generator - Genera dashboard semplificata per temi
Per ogni macro tema: lista ultimi report per company + recap pensiero aggregato

Autore: Senior Python Developer
Data: 23 Dicembre 2025
"""

import os
from typing import Dict, List
from datetime import datetime
from pathlib import Path
from jinja2 import Template

from topic_pipeline import TopicData
from source_registry import SourceRegistry
import utils


class DashboardGenerator:
    """
    Genera dashboard HTML moderna organizzata per topic.
    Per ogni topic mostra:
    - Lista ultimi report per company
    - Recap del pensiero aggregato
    """
    
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = Path(__file__).parent / 'output'
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = utils.logger
    
    def generate_dashboard(self, 
                           topics_data: Dict[str, TopicData],
                           source_registry: SourceRegistry) -> str:
        """
        Genera dashboard HTML completa
        
        Args:
            topics_data: Dati per ogni topic
            source_registry: Registry delle fonti
        
        Returns:
            Path al file HTML generato
        """
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"🎨 GENERATING DASHBOARD")
        self.logger.info(f"   Topics: {len(topics_data)}")
        self.logger.info(f"{'='*80}\n")
        
        # Prepara dati per template
        topics = []
        
        for topic_name, data in sorted(topics_data.items()):
            if not data.reports and not data.insights:
                continue
            
            # Organizza report per source
            reports_by_source = {}
            for report in data.reports:
                source = report.get('source', 'Unknown')
                if source not in reports_by_source:
                    reports_by_source[source] = []
                reports_by_source[source].append(report)
            
            # Top insights
            top_insights = data.insights[:5]
            
            topics.append({
                'name': topic_name,
                'slug': topic_name.lower().replace(' ', '-'),
                'sources': data.sources,
                'source_count': len(data.sources),
                'report_count': len(data.reports),
                'insight_count': len(data.insights),
                'reports_by_source': reports_by_source,
                'top_insights': top_insights,
                'narrative': data.narrative,
                'last_updated': data.last_updated[:10] if data.last_updated else 'N/A'
            })
        
        # Statistiche generali
        stats = {
            'total_topics': len(topics),
            'total_sources': len(source_registry.sources),
            'total_reports': sum(t['report_count'] for t in topics),
            'total_insights': sum(t['insight_count'] for t in topics)
        }
        
        # Genera HTML
        html = self._render_dashboard(topics, stats, source_registry)
        
        # Salva
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"dashboard_{timestamp}.html"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Crea anche index.html come latest
        index_path = self.output_dir / 'index.html'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        self.logger.info(f"✅ Dashboard salvata: {filepath}")
        self.logger.info(f"✅ Index aggiornato: {index_path}")
        
        return str(filepath)
    
    def _render_dashboard(self, topics: List[Dict], stats: Dict, 
                          source_registry: SourceRegistry) -> str:
        """Renderizza HTML dashboard"""
        
        template = Template('''
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global Insight Tracker - Dashboard</title>
    <style>
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #8b5cf6;
            --accent: #06b6d4;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --dark: #1e1b4b;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-500: #6b7280;
            --gray-800: #1f2937;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--gray-100);
            color: var(--gray-800);
            line-height: 1.6;
        }
        
        /* Navigation */
        .navbar {
            background: linear-gradient(135deg, var(--dark) 0%, var(--primary-dark) 100%);
            color: white;
            padding: 1rem 2rem;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        .navbar-content {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .logo-icon {
            font-size: 2rem;
        }
        
        .nav-stats {
            display: flex;
            gap: 2rem;
            font-size: 0.9rem;
        }
        
        .nav-stat {
            text-align: center;
        }
        
        .nav-stat-value {
            font-size: 1.5rem;
            font-weight: 700;
        }
        
        /* Topic Navigation */
        .topic-nav {
            background: white;
            padding: 1rem 2rem;
            border-bottom: 1px solid var(--gray-200);
            overflow-x: auto;
            white-space: nowrap;
        }
        
        .topic-nav-inner {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            gap: 0.75rem;
        }
        
        .topic-pill {
            display: inline-block;
            padding: 0.5rem 1rem;
            background: var(--gray-100);
            color: var(--gray-800);
            border-radius: 9999px;
            text-decoration: none;
            font-size: 0.875rem;
            font-weight: 500;
            transition: all 0.2s;
            border: 2px solid transparent;
        }
        
        .topic-pill:hover {
            background: var(--primary);
            color: white;
            transform: translateY(-2px);
        }
        
        .topic-pill.active {
            background: var(--primary);
            color: white;
        }
        
        /* Main Content */
        .main {
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 2rem;
        }
        
        /* Topic Section */
        .topic-section {
            margin-bottom: 3rem;
            scroll-margin-top: 120px;
        }
        
        .topic-header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 2rem;
            border-radius: 1rem 1rem 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .topic-title {
            font-size: 1.75rem;
            font-weight: 700;
        }
        
        .topic-badges {
            display: flex;
            gap: 1rem;
        }
        
        .badge {
            background: rgba(255,255,255,0.2);
            padding: 0.5rem 1rem;
            border-radius: 9999px;
            font-size: 0.875rem;
        }
        
        .topic-body {
            background: white;
            border-radius: 0 0 1rem 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        /* Narrative Section */
        .narrative {
            padding: 2rem;
            border-bottom: 1px solid var(--gray-200);
        }
        
        .narrative h3 {
            color: var(--primary);
            margin-bottom: 1rem;
            font-size: 1.1rem;
        }
        
        .narrative-text {
            color: var(--gray-800);
            white-space: pre-wrap;
            line-height: 1.8;
        }
        
        /* Sources Grid */
        .sources-section {
            padding: 2rem;
        }
        
        .sources-section h3 {
            color: var(--primary);
            margin-bottom: 1.5rem;
            font-size: 1.1rem;
        }
        
        .sources-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
        }
        
        .source-card {
            background: var(--gray-100);
            border-radius: 0.75rem;
            padding: 1.5rem;
            transition: all 0.2s;
        }
        
        .source-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        
        .source-name {
            font-weight: 700;
            font-size: 1.1rem;
            color: var(--primary-dark);
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--primary);
        }
        
        .report-item {
            padding: 0.75rem 0;
            border-bottom: 1px solid var(--gray-200);
        }
        
        .report-item:last-child {
            border-bottom: none;
        }
        
        .report-title {
            color: var(--gray-800);
            text-decoration: none;
            font-weight: 500;
            display: block;
            margin-bottom: 0.25rem;
        }
        
        .report-title:hover {
            color: var(--primary);
        }
        
        .report-summary {
            font-size: 0.85rem;
            color: var(--gray-500);
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        /* Insights Section */
        .insights-section {
            padding: 2rem;
            background: var(--gray-100);
            border-top: 1px solid var(--gray-200);
        }
        
        .insights-section h3 {
            color: var(--primary);
            margin-bottom: 1.5rem;
            font-size: 1.1rem;
        }
        
        .insight-card {
            background: white;
            padding: 1.25rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            border-left: 4px solid var(--primary);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .insight-text {
            margin-bottom: 0.5rem;
        }
        
        .insight-source {
            font-size: 0.8rem;
            color: var(--gray-500);
        }
        
        /* Footer */
        .footer {
            background: var(--dark);
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .navbar-content {
                flex-direction: column;
                gap: 1rem;
            }
            
            .nav-stats {
                gap: 1rem;
            }
            
            .topic-header {
                flex-direction: column;
                gap: 1rem;
                text-align: center;
            }
            
            .sources-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="navbar-content">
            <div class="logo">
                <span class="logo-icon">🌍</span>
                <span>Global Insight Tracker</span>
            </div>
            <div class="nav-stats">
                <div class="nav-stat">
                    <div class="nav-stat-value">{{ stats.total_topics }}</div>
                    <div>Topics</div>
                </div>
                <div class="nav-stat">
                    <div class="nav-stat-value">{{ stats.total_sources }}</div>
                    <div>Sources</div>
                </div>
                <div class="nav-stat">
                    <div class="nav-stat-value">{{ stats.total_reports }}</div>
                    <div>Reports</div>
                </div>
                <div class="nav-stat">
                    <div class="nav-stat-value">{{ stats.total_insights }}</div>
                    <div>Insights</div>
                </div>
            </div>
        </div>
    </nav>
    
    <!-- Topic Navigation -->
    <div class="topic-nav">
        <div class="topic-nav-inner">
            {% for topic in topics %}
            <a href="#{{ topic.slug }}" class="topic-pill">
                {{ topic.name }} ({{ topic.report_count }})
            </a>
            {% endfor %}
        </div>
    </div>
    
    <!-- Main Content -->
    <main class="main">
        {% for topic in topics %}
        <section class="topic-section" id="{{ topic.slug }}">
            <div class="topic-header">
                <h2 class="topic-title">{{ topic.name }}</h2>
                <div class="topic-badges">
                    <span class="badge">📄 {{ topic.report_count }} Reports</span>
                    <span class="badge">💡 {{ topic.insight_count }} Insights</span>
                    <span class="badge">🏢 {{ topic.source_count }} Sources</span>
                </div>
            </div>
            
            <div class="topic-body">
                <!-- Narrative -->
                {% if topic.narrative %}
                <div class="narrative">
                    <h3>📖 Executive Summary</h3>
                    <div class="narrative-text">{{ topic.narrative }}</div>
                </div>
                {% endif %}
                
                <!-- Reports by Source -->
                <div class="sources-section">
                    <h3>📚 Latest Reports by Company</h3>
                    <div class="sources-grid">
                        {% for source_name, reports in topic.reports_by_source.items() %}
                        <div class="source-card">
                            <div class="source-name">{{ source_name }}</div>
                            {% for report in reports[:3] %}
                            <div class="report-item">
                                <a href="{{ report.url }}" target="_blank" class="report-title">
                                    {{ report.title[:80] }}{% if report.title|length > 80 %}...{% endif %}
                                </a>
                                {% if report.summary %}
                                <div class="report-summary">{{ report.summary[:150] }}...</div>
                                {% endif %}
                            </div>
                            {% endfor %}
                        </div>
                        {% endfor %}
                    </div>
                </div>
                
                <!-- Top Insights -->
                {% if topic.top_insights %}
                <div class="insights-section">
                    <h3>💡 Key Insights (Aggregated View)</h3>
                    {% for insight in topic.top_insights %}
                    <div class="insight-card">
                        <div class="insight-text">{{ insight.text }}</div>
                        <div class="insight-source">
                            📄 {{ insight.source }} • {{ insight.report[:50] }}...
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
        </section>
        {% endfor %}
    </main>
    
    <!-- Footer -->
    <footer class="footer">
        <p>🌍 Global Insight Tracker - AI-Powered Intelligence Aggregation</p>
        <p>Generated on {{ timestamp }}</p>
    </footer>
    
    <script>
        // Highlight active topic on scroll
        document.addEventListener('scroll', function() {
            const sections = document.querySelectorAll('.topic-section');
            const pills = document.querySelectorAll('.topic-pill');
            
            let currentSection = '';
            
            sections.forEach(section => {
                const rect = section.getBoundingClientRect();
                if (rect.top <= 150) {
                    currentSection = section.id;
                }
            });
            
            pills.forEach(pill => {
                pill.classList.remove('active');
                if (pill.getAttribute('href') === '#' + currentSection) {
                    pill.classList.add('active');
                }
            });
        });
    </script>
</body>
</html>
''')
        
        return template.render(
            topics=topics,
            stats=stats,
            sources=list(source_registry.sources.values()),
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
