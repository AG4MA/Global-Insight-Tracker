# -*- coding: utf-8 -*-
"""
Topic Classifier - Classificazione articoli per topic
"""

from typing import Dict, List
from ..core.config import TOPICS, RELEVANCE_KEYWORDS
from ..core.utils import logger


class TopicClassifier:
    """
    Classificatore articoli per topic
    
    Usa keyword matching per assegnare topic agli articoli.
    """
    
    # Mapping keyword -> topic
    TOPIC_KEYWORDS = {
        'Artificial Intelligence': [
            'ai', 'artificial intelligence', 'machine learning', 
            'deep learning', 'neural network', 'nlp', 'computer vision'
        ],
        'Generative AI': [
            'generative ai', 'genai', 'llm', 'large language model',
            'gpt', 'chatgpt', 'claude', 'gemini', 'copilot', 'diffusion'
        ],
        'Cloud Computing': [
            'cloud', 'aws', 'azure', 'gcp', 'saas', 'paas', 'iaas',
            'serverless', 'kubernetes', 'containers'
        ],
        'Cybersecurity': [
            'cyber', 'security', 'ransomware', 'zero trust', 
            'threat', 'breach', 'encryption', 'phishing'
        ],
        'Digital Transformation': [
            'digital transformation', 'digitalization', 'automation',
            'digital strategy', 'modernization'
        ],
        'Data Analytics': [
            'data', 'analytics', 'big data', 'data science',
            'business intelligence', 'visualization', 'dashboard'
        ],
        'Blockchain': [
            'blockchain', 'web3', 'crypto', 'defi', 'nft',
            'smart contract', 'decentralized'
        ],
        'Internet of Things': [
            'iot', 'internet of things', 'edge computing', 
            'smart devices', 'sensors', 'connected'
        ],
        'Quantum Computing': [
            'quantum', 'qubits', 'quantum computing',
            'quantum advantage', 'superposition'
        ],
        'Sustainability': [
            'sustainability', 'esg', 'green tech', 'climate',
            'carbon', 'renewable', 'net zero'
        ],
        'Future of Work': [
            'future of work', 'remote work', 'hybrid',
            'workforce', 'talent', 'skills', 'upskilling'
        ],
    }
    
    def classify(self, article: Dict) -> str:
        """
        Classifica singolo articolo
        
        Args:
            article: Dizionario articolo
            
        Returns:
            Topic assegnato
        """
        text = f"{article.get('title', '')} {article.get('description', '')}".lower()
        
        scores = {}
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[topic] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return article.get('category', 'General')
    
    def classify_all(self, articles: List[Dict]) -> List[Dict]:
        """
        Classifica tutti gli articoli
        
        Args:
            articles: Lista articoli
            
        Returns:
            Articoli con topic aggiunto
        """
        for article in articles:
            article['topic'] = self.classify(article)
        
        return articles
    
    def group_by_topic(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Raggruppa articoli per topic
        
        Args:
            articles: Lista articoli (già classificati)
            
        Returns:
            Dict topic -> lista articoli
        """
        groups = {}
        
        for article in articles:
            topic = article.get('topic', 'General')
            if topic not in groups:
                groups[topic] = []
            groups[topic].append(article)
        
        return groups
    
    def get_topic_stats(self, articles: List[Dict]) -> Dict[str, int]:
        """
        Conta articoli per topic
        
        Args:
            articles: Lista articoli
            
        Returns:
            Dict topic -> count
        """
        groups = self.group_by_topic(articles)
        return {topic: len(arts) for topic, arts in groups.items()}
