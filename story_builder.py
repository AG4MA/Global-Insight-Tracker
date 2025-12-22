# -*- coding: utf-8 -*-
"""
Story Builder - Crea narrative aggregate per topic
Combina insights da multiple fonti in storytelling coerente

Autore: Senior Python Developer
Data: 22 Dicembre 2025
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict
import utils


class StoryBuilder:
    """Costruisce narrative aggregate per topic"""
    
    def __init__(self, ai_analyzer=None):
        """
        Args:
            ai_analyzer: Istanza di AIAnalyzer per generare narrative (opzionale)
        """
        self.ai_analyzer = ai_analyzer
        self.logger = utils.logger
    
    def build_topic_stories(self, analyses: List[Dict]) -> Dict[str, Dict]:
        """
        Aggrega analisi per topic e crea stories
        
        Args:
            analyses: Lista di analisi AI dei documenti
        
        Returns:
            Dict con topic come key e story come value
        """
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"📖 Building Topic Stories from {len(analyses)} analyses")
        self.logger.info(f"{'='*80}\n")
        
        # Raggruppa per topic
        topic_groups = self._group_by_topic(analyses)
        
        self.logger.info(f"📊 Topics trovati: {len(topic_groups)}")
        for topic, docs in topic_groups.items():
            self.logger.info(f"  • {topic}: {len(docs)} documenti")
        
        # Crea story per ogni topic
        stories = {}
        
        for topic, topic_analyses in topic_groups.items():
            self.logger.info(f"\n📖 Creando story per: {topic}")
            
            story = self._build_topic_story(topic, topic_analyses)
            stories[topic] = story
            
            self.logger.info(f"  ✅ Story completata: {len(story['insights'])} insights aggregati")
        
        return stories
    
    def _group_by_topic(self, analyses: List[Dict]) -> Dict[str, List[Dict]]:
        """Raggruppa analisi per topic"""
        
        topic_groups = defaultdict(list)
        
        for analysis in analyses:
            topics = analysis.get('topics', [])
            
            # Ogni analisi può appartenere a multipli topics
            for topic in topics:
                topic_groups[topic].append(analysis)
        
        return dict(topic_groups)
    
    def _build_topic_story(self, topic: str, analyses: List[Dict]) -> Dict:
        """
        Costruisce story per un singolo topic
        
        Args:
            topic: Nome del topic
            analyses: Lista di analisi per questo topic
        
        Returns:
            Dict con la story strutturata
        """
        # Aggrega informazioni
        all_insights = []
        all_technologies = set()
        all_trends = set()
        sources = []
        sentiments = defaultdict(int)
        
        for analysis in analyses:
            # Insights
            insights = analysis.get('key_insights', [])
            for insight in insights:
                all_insights.append({
                    'text': insight,
                    'source': analysis.get('source_document', 'Unknown'),
                    'confidence': analysis.get('confidence', 'medium')
                })
            
            # Technologies
            techs = analysis.get('technologies', [])
            all_technologies.update(techs)
            
            # Trends
            trends = analysis.get('trends', [])
            all_trends.update(trends)
            
            # Sources
            source_doc = analysis.get('source_document', 'Unknown')
            if source_doc not in sources:
                sources.append(source_doc)
            
            # Sentiment
            sentiment = analysis.get('sentiment', 'neutral')
            sentiments[sentiment] += 1
        
        # Determina sentiment prevalente
        prevalent_sentiment = max(sentiments, key=sentiments.get) if sentiments else 'neutral'
        
        # Ranking insights per confidence
        high_confidence_insights = [i for i in all_insights if i['confidence'] == 'high']
        medium_confidence_insights = [i for i in all_insights if i['confidence'] == 'medium']
        low_confidence_insights = [i for i in all_insights if i['confidence'] == 'low']
        
        ranked_insights = high_confidence_insights + medium_confidence_insights + low_confidence_insights
        
        # Genera narrative usando AI se disponibile
        if self.ai_analyzer:
            narrative = self._generate_ai_narrative(topic, ranked_insights, analyses)
        else:
            narrative = self._generate_simple_narrative(topic, ranked_insights)
        
        # Costruisci story
        story = {
            'topic': topic,
            'narrative': narrative,
            'insights': ranked_insights,
            'top_insights': ranked_insights[:5],  # Top 5
            'technologies': sorted(list(all_technologies)),
            'trends': sorted(list(all_trends)),
            'sources': sources,
            'document_count': len(analyses),
            'sentiment': prevalent_sentiment,
            'created_at': datetime.now().isoformat(),
            'metadata': {
                'total_insights': len(all_insights),
                'high_confidence': len(high_confidence_insights),
                'medium_confidence': len(medium_confidence_insights),
                'low_confidence': len(low_confidence_insights)
            }
        }
        
        return story
    
    def _generate_ai_narrative(self, topic: str, insights: List[Dict], analyses: List[Dict]) -> str:
        """Genera narrative usando AI"""
        
        self.logger.info(f"  🤖 Generando narrative AI per {topic}...")
        
        # Prepara context per AI
        insights_text = "\n".join([f"- {i['text']}" for i in insights[:10]])  # Top 10
        
        summaries = []
        for analysis in analyses:
            summary = analysis.get('summary', '')
            if summary:
                summaries.append(summary[:300])  # Prime 300 char
        
        summaries_text = "\n\n".join(summaries[:5])  # Max 5 summaries
        
        prompt = f"""Crea una narrative coerente e avvincente sul topic "{topic}" basata su questi insights estratti da report di consulenza di multiple aziende.

KEY INSIGHTS:
{insights_text}

SUMMARIES DEI DOCUMENTI:
{summaries_text}

Crea una narrative (300-400 parole) che:
1. Introduca il topic e la sua rilevanza attuale
2. Integri gli insights in un racconto coerente
3. Evidenzi trend emergenti e implicazioni
4. Sia scritta in tono professionale ma accessibile
5. Concluda con prospettive future

Narrative:"""
        
        try:
            narrative = self.ai_analyzer._call_llm(prompt, max_tokens=600)
            return narrative.strip()
        except Exception as e:
            self.logger.error(f"  ❌ Errore generazione narrative AI: {e}")
            return self._generate_simple_narrative(topic, insights)
    
    def _generate_simple_narrative(self, topic: str, insights: List[Dict]) -> str:
        """Genera narrative semplice senza AI"""
        
        narrative = f"""## {topic}: Panoramica Insights

Dall'analisi di {len(insights)} insights raccolti da diverse fonti, emergono tendenze significative nel campo di {topic}.

"""
        
        # Aggiungi top insights
        if insights:
            narrative += "**Key Findings:**\n\n"
            for i, insight in enumerate(insights[:5], 1):
                narrative += f"{i}. {insight['text']}\n"
        
        narrative += f"\nQuesti insights riflettono la crescente importanza di {topic} nel panorama tecnologico e business attuale."
        
        return narrative
    
    def export_stories(self, stories: Dict[str, Dict], output_dir: str) -> str:
        """
        Esporta stories in JSON
        
        Args:
            stories: Dict di stories
            output_dir: Directory di output
        
        Returns:
            Path al file JSON
        """
        import os
        from pathlib import Path
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"topic_stories_{timestamp}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stories, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 Stories salvate: {filepath}")
        
        return str(filepath)
    
    def get_topic_summary(self, stories: Dict[str, Dict]) -> Dict:
        """
        Genera summary di tutti i topics
        
        Returns:
            Dict con statistiche aggregate
        """
        summary = {
            'total_topics': len(stories),
            'topics': list(stories.keys()),
            'total_documents': sum(s['document_count'] for s in stories.values()),
            'total_insights': sum(len(s['insights']) for s in stories.values()),
            'by_topic': {}
        }
        
        for topic, story in stories.items():
            summary['by_topic'][topic] = {
                'documents': story['document_count'],
                'insights': len(story['insights']),
                'sentiment': story['sentiment'],
                'technologies': len(story['technologies']),
                'sources': story['sources']
            }
        
        return summary
