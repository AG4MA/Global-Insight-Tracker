# -*- coding: utf-8 -*-
"""
Final Dashboard - Dashboard completa con riassunti per topic
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List
import json

from ..core.config import OUTPUT_DIR
from ..core.utils import logger


class FinalDashboard:
    """
    Genera dashboard HTML completa con:
    - Vista per TOPIC
    - Lista articoli per company
    - Riassunti individuali
    - Recap aggregato per topic
    """
    
    def __init__(self, filename: str = "final_dashboard.html"):
        self.filepath = OUTPUT_DIR / filename
        self.json_path = OUTPUT_DIR / "insights_data.json"
    
    def generate(
        self, 
        articles: List[Dict], 
        topic_groups: Dict[str, List],
        topic_recaps: Dict[str, str] = None
    ) -> bool:
        """
        Genera dashboard finale.
        
        Args:
            articles: Tutti gli articoli con summary
            topic_groups: Articoli raggruppati per topic
            topic_recaps: Recap aggregati per topic
            
        Returns:
            True se successo
        """
        try:
            # Salva anche JSON per uso programmatico
            self._save_json(articles, topic_groups, topic_recaps)
            
            # Genera HTML
            html = self._build_html(articles, topic_groups, topic_recaps or {})
            
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"✅ Final Dashboard: {self.filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Dashboard generation failed: {e}")
            return False
    
    def _save_json(self, articles, topic_groups, topic_recaps):
        """Salva dati in JSON"""
        data = {
            'generated_at': datetime.now().isoformat(),
            'total_articles': len(articles),
            'topics': list(topic_groups.keys()),
            'articles': articles,
            'topic_recaps': topic_recaps or {},
        }
        
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _build_html(self, articles, topic_groups, topic_recaps) -> str:
        """Costruisce HTML completo"""
        
        # Statistiche
        total = len(articles)
        with_summary = sum(1 for a in articles if a.get('summary'))
        sources = list(set(a.get('source', '') for a in articles))
        
        # Genera sezioni per topic
        topic_sections = []
        for topic in sorted(topic_groups.keys(), key=lambda t: len(topic_groups[t]), reverse=True):
            topic_articles = topic_groups[topic]
            recap = topic_recaps.get(topic, '')
            section = self._build_topic_section(topic, topic_articles, recap)
            topic_sections.append(section)
        
        return f'''<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global Insight Tracker - Final Dashboard</title>
    <style>
        :root {{
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --secondary: #64748b;
            --success: #22c55e;
            --warning: #f59e0b;
            --bg: #f1f5f9;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-light: #64748b;
            --border: #e2e8f0;
        }}
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }}
        
        .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            padding: 3rem 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 20px rgba(37, 99, 235, 0.3);
        }}
        .header h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .header .subtitle {{ opacity: 0.9; font-size: 1.1rem; }}
        .header .meta {{ margin-top: 1rem; font-size: 0.9rem; opacity: 0.8; }}
        
        /* Stats Grid */
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
            text-align: center;
        }}
        .stat-card .label {{ color: var(--text-light); font-size: 0.875rem; margin-bottom: 0.25rem; }}
        .stat-card .value {{ font-size: 2.5rem; font-weight: 700; color: var(--primary); }}
        
        /* Navigation */
        .nav {{
            background: var(--card-bg);
            padding: 1rem;
            border-radius: 0.75rem;
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            position: sticky;
            top: 1rem;
            z-index: 100;
        }}
        .nav-title {{ font-weight: 600; margin-bottom: 0.5rem; color: var(--text-light); }}
        .nav-links {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
        .nav-link {{
            display: inline-block;
            padding: 0.5rem 1rem;
            background: var(--bg);
            border-radius: 0.5rem;
            text-decoration: none;
            color: var(--text);
            font-size: 0.875rem;
            transition: all 0.2s;
        }}
        .nav-link:hover {{ background: var(--primary); color: white; }}
        .nav-link .count {{ 
            background: var(--primary); 
            color: white; 
            padding: 0.125rem 0.5rem; 
            border-radius: 1rem; 
            font-size: 0.75rem;
            margin-left: 0.25rem;
        }}
        .nav-link:hover .count {{ background: white; color: var(--primary); }}
        
        /* Topic Section */
        .topic-section {{
            background: var(--card-bg);
            border-radius: 1rem;
            margin-bottom: 2rem;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .topic-header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            padding: 1.5rem 2rem;
        }}
        .topic-header h2 {{ font-size: 1.5rem; margin-bottom: 0.25rem; }}
        .topic-header .topic-meta {{ opacity: 0.9; font-size: 0.9rem; }}
        
        /* Recap Box */
        .recap-box {{
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-left: 4px solid var(--warning);
            padding: 1.5rem 2rem;
            margin: 0;
        }}
        .recap-box h3 {{ 
            color: #92400e; 
            font-size: 1rem; 
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .recap-box .recap-content {{ 
            color: #78350f; 
            font-size: 0.95rem;
            line-height: 1.7;
        }}
        .recap-box .recap-content strong {{ color: #92400e; }}
        
        /* Articles by Source */
        .source-group {{
            border-bottom: 1px solid var(--border);
            padding: 1.5rem 2rem;
        }}
        .source-group:last-child {{ border-bottom: none; }}
        .source-name {{
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 1rem;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .source-name .badge {{
            background: var(--primary);
            color: white;
            padding: 0.125rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            font-weight: 500;
        }}
        
        /* Article Card */
        .article {{
            background: var(--bg);
            border-radius: 0.75rem;
            padding: 1.25rem;
            margin-bottom: 1rem;
        }}
        .article:last-child {{ margin-bottom: 0; }}
        .article-title {{
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        .article-title a {{
            color: var(--text);
            text-decoration: none;
        }}
        .article-title a:hover {{ color: var(--primary); }}
        .article-summary {{
            color: var(--text-light);
            font-size: 0.9rem;
            line-height: 1.6;
            margin-top: 0.75rem;
            padding-top: 0.75rem;
            border-top: 1px solid var(--border);
        }}
        .article-summary strong {{ color: var(--text); }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-light);
            font-size: 0.875rem;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .container {{ padding: 1rem; }}
            .header h1 {{ font-size: 1.75rem; }}
            .stats {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 Global Insight Tracker</h1>
            <p class="subtitle">Dashboard insights su tecnologie dirompenti dalle principali società di consulenza</p>
            <p class="meta">📅 Generato: {datetime.now().strftime('%d/%m/%Y alle %H:%M')} | 
               📊 {len(sources)} fonti analizzate</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="label">Articoli Totali</div>
                <div class="value">{total}</div>
            </div>
            <div class="stat-card">
                <div class="label">Con Riassunto</div>
                <div class="value">{with_summary}</div>
            </div>
            <div class="stat-card">
                <div class="label">Topic</div>
                <div class="value">{len(topic_groups)}</div>
            </div>
            <div class="stat-card">
                <div class="label">Fonti</div>
                <div class="value">{len(sources)}</div>
            </div>
        </div>
        
        <nav class="nav">
            <div class="nav-title">🏷️ Naviga per Topic</div>
            <div class="nav-links">
                {self._build_nav_links(topic_groups)}
            </div>
        </nav>
        
        {"".join(topic_sections)}
        
        <footer class="footer">
            <p>Global Insight Tracker v2.1 | Generato automaticamente con AI</p>
            <p>I riassunti sono generati da AI e potrebbero contenere imprecisioni.</p>
        </footer>
    </div>
</body>
</html>'''
    
    def _build_nav_links(self, topic_groups: Dict) -> str:
        """Costruisce link navigazione"""
        links = []
        for topic in sorted(topic_groups.keys(), key=lambda t: len(topic_groups[t]), reverse=True):
            count = len(topic_groups[topic])
            topic_id = topic.lower().replace(' ', '-').replace('&', 'and')
            links.append(f'<a href="#{topic_id}" class="nav-link">{topic}<span class="count">{count}</span></a>')
        return '\n'.join(links)
    
    def _build_topic_section(self, topic: str, articles: List[Dict], recap: str) -> str:
        """Costruisce sezione per un topic"""
        topic_id = topic.lower().replace(' ', '-').replace('&', 'and')
        
        # Raggruppa per source
        by_source = {}
        for art in articles:
            source = art.get('source', 'Unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(art)
        
        # Costruisci gruppi per source
        source_groups = []
        for source in sorted(by_source.keys()):
            arts = by_source[source]
            source_groups.append(self._build_source_group(source, arts))
        
        # Recap box
        recap_html = ''
        if recap:
            # Converti markdown-like in HTML
            recap_formatted = recap.replace('\n\n', '</p><p>').replace('\n', '<br>')
            recap_formatted = f'<p>{recap_formatted}</p>'
            recap_html = f'''
            <div class="recap-box">
                <h3>💡 Recap Aggregato - Cosa dicono le Company</h3>
                <div class="recap-content">{recap_formatted}</div>
            </div>'''
        
        return f'''
        <section class="topic-section" id="{topic_id}">
            <div class="topic-header">
                <h2>📁 {topic}</h2>
                <p class="topic-meta">{len(articles)} articoli da {len(by_source)} fonti</p>
            </div>
            {recap_html}
            {"".join(source_groups)}
        </section>'''
    
    def _build_source_group(self, source: str, articles: List[Dict]) -> str:
        """Costruisce gruppo articoli per source"""
        articles_html = []
        
        for art in articles[:5]:  # Max 5 per source
            title = art.get('title', 'Untitled')
            url = art.get('url', '#')
            summary = art.get('summary', '')
            
            summary_html = ''
            if summary:
                # Formatta summary
                summary_formatted = summary.replace('\n', '<br>')
                summary_html = f'<div class="article-summary">{summary_formatted}</div>'
            
            articles_html.append(f'''
            <div class="article">
                <div class="article-title">
                    <a href="{url}" target="_blank">{title}</a>
                </div>
                {summary_html}
            </div>''')
        
        return f'''
        <div class="source-group">
            <div class="source-name">
                🏢 {source}
                <span class="badge">{len(articles)} articoli</span>
            </div>
            {"".join(articles_html)}
        </div>'''
