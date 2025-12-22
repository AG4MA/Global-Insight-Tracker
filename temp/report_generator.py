# -*- coding: utf-8 -*-
"""
Report Generator - Genera report HTML e Excel organizzati per TOPIC
Non più per fonte, ma aggregati per argomento con storytelling

Autore: Senior Python Developer
Data: 22 Dicembre 2025
"""

import os
from typing import Dict, List
from datetime import datetime
from pathlib import Path
import pandas as pd
from jinja2 import Template

import utils


class TopicReportGenerator:
    """Genera report organizzati per topic"""
    
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(__file__), 'output')
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.logger = utils.logger
    
    def generate_html_report(self, stories: Dict[str, Dict], summary: Dict) -> str:
        """
        Genera report HTML interattivo organizzato per topic
        
        Args:
            stories: Dict di stories per topic
            summary: Summary statistiche
        
        Returns:
            Path al file HTML
        """
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"📊 Generando Report HTML per Topics")
        self.logger.info(f"{'='*80}\n")
        
        # Template HTML
        html_template = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global Insight Tracker - Topic Intelligence</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .summary {
            background: #f8f9fa;
            padding: 30px;
            border-bottom: 3px solid #667eea;
        }
        
        .summary h2 {
            color: #667eea;
            margin-bottom: 20px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-card h3 {
            font-size: 2.5em;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .stat-card p {
            color: #666;
            font-size: 0.9em;
        }
        
        .topics-nav {
            background: #fff;
            padding: 20px;
            border-bottom: 1px solid #e0e0e0;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .topics-nav h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .topic-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .topic-pill {
            background: #667eea;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            text-decoration: none;
            font-size: 0.9em;
            transition: all 0.3s;
        }
        
        .topic-pill:hover {
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        .content {
            padding: 40px;
        }
        
        .topic-section {
            margin-bottom: 60px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 40px;
        }
        
        .topic-section:last-child {
            border-bottom: none;
        }
        
        .topic-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        
        .topic-header h2 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .topic-meta {
            display: flex;
            gap: 20px;
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .narrative {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            border-left: 5px solid #667eea;
        }
        
        .narrative h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .insights {
            margin-bottom: 30px;
        }
        
        .insights h3 {
            color: #667eea;
            margin-bottom: 20px;
        }
        
        .insight-card {
            background: white;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            transition: all 0.3s;
        }
        
        .insight-card:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        
        .insight-text {
            font-size: 1.05em;
            margin-bottom: 10px;
        }
        
        .insight-meta {
            font-size: 0.85em;
            color: #666;
        }
        
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .badge-high {
            background: #4caf50;
            color: white;
        }
        
        .badge-medium {
            background: #ff9800;
            color: white;
        }
        
        .badge-low {
            background: #9e9e9e;
            color: white;
        }
        
        .tech-tags {
            margin-bottom: 20px;
        }
        
        .tech-tags h4 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 0.9em;
        }
        
        .tag {
            display: inline-block;
            background: #e3f2fd;
            color: #1976d2;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            margin: 5px 5px 5px 0;
        }
        
        .sources {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .sources h4 {
            color: #666;
            margin-bottom: 10px;
            font-size: 0.9em;
        }
        
        .sources ul {
            list-style: none;
            padding-left: 0;
        }
        
        .sources li {
            padding: 5px 0;
            color: #666;
            font-size: 0.9em;
        }
        
        .sources li:before {
            content: "📄 ";
            margin-right: 5px;
        }
        
        footer {
            background: #333;
            color: white;
            text-align: center;
            padding: 20px;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            header h1 {
                font-size: 1.8em;
            }
            
            .stats {
                grid-template-columns: 1fr;
            }
            
            .topic-pills {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌍 Global Insight Tracker</h1>
            <p>Intelligence Report Aggregato per Topic | {{ timestamp }}</p>
        </header>
        
        <div class="summary">
            <h2>📊 Executive Summary</h2>
            <div class="stats">
                <div class="stat-card">
                    <h3>{{ summary.total_topics }}</h3>
                    <p>Topics Analizzati</p>
                </div>
                <div class="stat-card">
                    <h3>{{ summary.total_documents }}</h3>
                    <p>Documenti Processati</p>
                </div>
                <div class="stat-card">
                    <h3>{{ summary.total_insights }}</h3>
                    <p>Insights Estratti</p>
                </div>
            </div>
        </div>
        
        <div class="topics-nav">
            <h3>🗂️ Navigate Topics</h3>
            <div class="topic-pills">
                {% for topic in summary.topics %}
                <a href="#{{ topic|replace(' ', '-') }}" class="topic-pill">{{ topic }}</a>
                {% endfor %}
            </div>
        </div>
        
        <div class="content">
            {% for topic, story in stories.items() %}
            <div class="topic-section" id="{{ topic|replace(' ', '-') }}">
                <div class="topic-header">
                    <h2>{{ topic }}</h2>
                    <div class="topic-meta">
                        <span>📄 {{ story.document_count }} documenti</span>
                        <span>💡 {{ story.insights|length }} insights</span>
                        <span>😊 Sentiment: {{ story.sentiment }}</span>
                    </div>
                </div>
                
                <div class="narrative">
                    <h3>📖 Narrative</h3>
                    <p style="white-space: pre-wrap;">{{ story.narrative }}</p>
                </div>
                
                {% if story.technologies %}
                <div class="tech-tags">
                    <h4>🔧 Tecnologie Menzionate:</h4>
                    {% for tech in story.technologies %}
                    <span class="tag">{{ tech }}</span>
                    {% endfor %}
                </div>
                {% endif %}
                
                {% if story.trends %}
                <div class="tech-tags">
                    <h4>📈 Trends Identificati:</h4>
                    {% for trend in story.trends %}
                    <span class="tag">{{ trend }}</span>
                    {% endfor %}
                </div>
                {% endif %}
                
                <div class="insights">
                    <h3>💡 Key Insights (Top {{ story.top_insights|length }})</h3>
                    {% for insight in story.top_insights %}
                    <div class="insight-card">
                        <div class="insight-text">{{ insight.text }}</div>
                        <div class="insight-meta">
                            <span class="badge badge-{{ insight.confidence }}">{{ insight.confidence }} confidence</span>
                            <span style="margin-left: 10px;">📄 {{ insight.source }}</span>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                
                <div class="sources">
                    <h4>📚 Fonti Documentali:</h4>
                    <ul>
                        {% for source in story.sources %}
                        <li>{{ source }}</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <footer>
            <p>Global Insight Tracker - AI-Powered Intelligence Aggregation</p>
            <p>Generated on {{ timestamp }}</p>
        </footer>
    </div>
</body>
</html>
"""
        
        # Renderizza template
        template = Template(html_template)
        
        html_content = template.render(
            stories=stories,
            summary=summary,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Salva file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"topic_report_{timestamp}.html"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"✅ Report HTML salvato: {filepath}")
        
        return str(filepath)
    
    def generate_excel_report(self, stories: Dict[str, Dict], summary: Dict) -> str:
        """
        Genera report Excel con sheet per ogni topic
        
        Args:
            stories: Dict di stories per topic
            summary: Summary statistiche
        
        Returns:
            Path al file Excel
        """
        self.logger.info(f"\n📊 Generando Report Excel per Topics\n")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"topic_report_{timestamp}.xlsx"
        filepath = self.output_dir / filename
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Sheet 1: Summary
            summary_data = {
                'Metric': [
                    'Total Topics',
                    'Total Documents',
                    'Total Insights',
                    'Report Generated'
                ],
                'Value': [
                    summary['total_topics'],
                    summary['total_documents'],
                    summary['total_insights'],
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
            }
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            
            # Sheet per ogni topic
            for topic, story in stories.items():
                # Prepara dati insights
                insights_data = []
                
                for insight in story['insights']:
                    insights_data.append({
                        'Insight': insight['text'],
                        'Source': insight['source'],
                        'Confidence': insight['confidence']
                    })
                
                if insights_data:
                    df_topic = pd.DataFrame(insights_data)
                    
                    # Limita nome sheet (Excel max 31 char)
                    sheet_name = topic[:31]
                    
                    df_topic.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    self.logger.info(f"  ✅ Sheet creato: {sheet_name}")
        
        self.logger.info(f"✅ Report Excel salvato: {filepath}\n")
        
        return str(filepath)
