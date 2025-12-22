# -*- coding: utf-8 -*-
"""
Story Builder - Generazione narrative aggregate per topic
"""

from typing import Dict, List
from ..core.utils import logger


class StoryBuilder:
    """
    Costruisce narrative aggregate per topic
    
    Combina articoli per creare un "racconto" del pensiero
    delle società di consulenza su ogni topic.
    """
    
    def build_topic_story(self, topic: str, articles: List[Dict]) -> Dict:
        """
        Costruisce story per un topic
        
        Args:
            topic: Nome topic
            articles: Articoli del topic
            
        Returns:
            Dict con story
        """
        if not articles:
            return {'topic': topic, 'count': 0, 'summary': '', 'sources': []}
        
        # Raggruppa per source
        by_source = {}
        for art in articles:
            src = art.get('source', 'Unknown')
            if src not in by_source:
                by_source[src] = []
            by_source[src].append(art)
        
        # Costruisci sommario
        summary_parts = []
        for source, arts in by_source.items():
            titles = [a.get('title', '')[:50] for a in arts[:3]]
            summary_parts.append(f"**{source}** ({len(arts)} articoli): {', '.join(titles)}")
        
        return {
            'topic': topic,
            'count': len(articles),
            'sources': list(by_source.keys()),
            'by_source': {src: len(arts) for src, arts in by_source.items()},
            'summary': '\n'.join(summary_parts),
            'articles': articles,
        }
    
    def build_all_stories(self, topic_groups: Dict[str, List]) -> List[Dict]:
        """
        Costruisce stories per tutti i topic
        
        Args:
            topic_groups: Dict topic -> articoli
            
        Returns:
            Lista stories
        """
        stories = []
        
        for topic, articles in topic_groups.items():
            story = self.build_topic_story(topic, articles)
            stories.append(story)
        
        # Ordina per numero articoli
        stories.sort(key=lambda x: x['count'], reverse=True)
        
        return stories
    
    def generate_report(self, stories: List[Dict]) -> str:
        """
        Genera report testuale
        
        Args:
            stories: Lista stories
            
        Returns:
            Report formattato
        """
        lines = [
            "=" * 60,
            "GLOBAL INSIGHT TRACKER - REPORT PER TOPIC",
            "=" * 60,
            ""
        ]
        
        for story in stories:
            lines.append(f"## {story['topic']} ({story['count']} articoli)")
            lines.append("-" * 40)
            
            if story.get('by_source'):
                for src, count in story['by_source'].items():
                    lines.append(f"  • {src}: {count} articoli")
            
            lines.append("")
        
        return '\n'.join(lines)
