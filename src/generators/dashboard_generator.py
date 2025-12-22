# -*- coding: utf-8 -*-
"""
Dashboard Generator - Generazione dashboard HTML
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List

from ..core.config import OUTPUT_DIR, OUTPUT, TOPICS
from ..core.utils import logger


class DashboardGenerator:
    """
    Generatore dashboard HTML interattiva
    """
    
    def __init__(self, filename: str = None):
        if filename is None:
            filename = OUTPUT.dashboard_filename
        self.filepath = OUTPUT_DIR / filename
    
    def generate(self, articles: List[Dict], topic_groups: Dict[str, List] = None) -> bool:
        """
        Genera dashboard HTML
        
        Args:
            articles: Lista articoli
            topic_groups: Articoli raggruppati per topic
            
        Returns:
            True se successo
        """
        try:
            html = self._build_html(articles, topic_groups or {})
            
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"✅ Dashboard: {self.filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Errore generazione dashboard: {e}")
            return False
    
    def _build_html(self, articles: List[Dict], topic_groups: Dict) -> str:
        """Costruisce HTML dashboard"""
        
        # Stats
        total = len(articles)
        sources = {}
        for art in articles:
            src = art.get('source', 'Unknown')
            sources[src] = sources.get(src, 0) + 1
        
        # HTML
        return f'''<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global Insight Tracker - Dashboard</title>
    <style>
        :root {{
            --primary: #2563eb;
            --secondary: #64748b;
            --success: #22c55e;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
        header {{
            background: linear-gradient(135deg, var(--primary), #1d4ed8);
            color: white;
            padding: 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
        }}
        header h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        header p {{ opacity: 0.9; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .stat-card {{
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .stat-card h3 {{ color: var(--secondary); font-size: 0.875rem; }}
        .stat-card .value {{ font-size: 2rem; font-weight: 700; color: var(--primary); }}
        .section {{ margin-bottom: 2rem; }}
        .section h2 {{
            font-size: 1.5rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--primary);
        }}
        .articles {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1rem;
        }}
        .article-card {{
            background: var(--card-bg);
            padding: 1.25rem;
            border-radius: 0.75rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .article-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .article-card h3 {{
            font-size: 1rem;
            margin-bottom: 0.5rem;
            line-height: 1.4;
        }}
        .article-card h3 a {{
            color: var(--text);
            text-decoration: none;
        }}
        .article-card h3 a:hover {{ color: var(--primary); }}
        .article-card .meta {{
            font-size: 0.75rem;
            color: var(--secondary);
            margin-bottom: 0.5rem;
        }}
        .article-card .source {{
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 0.125rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            margin-right: 0.5rem;
        }}
        .article-card .topic {{
            display: inline-block;
            background: var(--success);
            color: white;
            padding: 0.125rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
        }}
        .article-card .description {{
            font-size: 0.875rem;
            color: var(--secondary);
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        footer {{
            text-align: center;
            padding: 2rem;
            color: var(--secondary);
            font-size: 0.875rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌐 Global Insight Tracker</h1>
            <p>Dashboard insights tecnologie dirompenti - Aggiornato: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Articoli Totali</h3>
                <div class="value">{total}</div>
            </div>
            <div class="stat-card">
                <h3>Fonti</h3>
                <div class="value">{len(sources)}</div>
            </div>
            <div class="stat-card">
                <h3>Topic</h3>
                <div class="value">{len(topic_groups)}</div>
            </div>
        </div>
        
        {self._build_articles_section(articles)}
        
        <footer>
            Global Insight Tracker v2.1 - Generato automaticamente
        </footer>
    </div>
</body>
</html>'''
    
    def _build_articles_section(self, articles: List[Dict]) -> str:
        """Costruisce sezione articoli"""
        if not articles:
            return '<p>Nessun articolo trovato.</p>'
        
        cards = []
        for art in articles[:50]:  # Limita a 50
            title = art.get('title', 'Untitled')[:100]
            url = art.get('url', '#')
            source = art.get('source', 'Unknown')
            topic = art.get('topic', art.get('category', 'General'))
            desc = art.get('description', '')[:200]
            
            cards.append(f'''
            <div class="article-card">
                <h3><a href="{url}" target="_blank">{title}</a></h3>
                <div class="meta">
                    <span class="source">{source}</span>
                    <span class="topic">{topic}</span>
                </div>
                <p class="description">{desc}</p>
            </div>''')
        
        return f'''
        <div class="section">
            <h2>📰 Ultimi Articoli</h2>
            <div class="articles">
                {"".join(cards)}
            </div>
        </div>'''
