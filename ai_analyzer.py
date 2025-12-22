# -*- coding: utf-8 -*-
"""
AI Analyzer - Analisi intelligente dei documenti con LLM
Estrae insights, categorizza per topic, genera summaries

Supporta OpenAI e Anthropic Claude

Autore: Senior Python Developer
Data: 22 Dicembre 2025
"""

import os
import re
import json
from typing import Dict, List, Optional
from datetime import datetime

# AI APIs
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

import utils


class AIAnalyzer:
    """Analizza documenti usando AI"""
    
    def __init__(self, provider: str = 'openai', api_key: Optional[str] = None):
        """
        Args:
            provider: 'openai' o 'anthropic'
            api_key: API key (o usa variabile ambiente)
        """
        self.provider = provider.lower()
        self.logger = utils.logger
        
        # Setup API
        if self.provider == 'openai':
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package non installato. pip install openai")
            
            self.api_key = api_key or os.getenv('OPENAI_API_KEY')
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY non trovata")
            
            openai.api_key = self.api_key
            self.model = 'gpt-4-turbo-preview'  # o gpt-3.5-turbo per risparmiare
        
        elif self.provider == 'anthropic':
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("anthropic package non installato. pip install anthropic")
            
            self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY non trovata")
            
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model = 'claude-3-sonnet-20240229'
        
        else:
            raise ValueError(f"Provider non supportato: {provider}")
    
    def analyze_document(self, parsed_doc: Dict, analysis_type: str = 'full') -> Dict:
        """
        Analizza documento con AI
        
        Args:
            parsed_doc: Documento parsato (da DocumentParser)
            analysis_type: 'full', 'summary', 'topics', 'insights'
        
        Returns:
            Dict con risultati analisi
        """
        text = parsed_doc.get('text', '')
        
        if not text or len(text) < 100:
            self.logger.warning(f"⚠️  Testo troppo breve per analisi: {len(text)} caratteri")
            return None
        
        # Tronca testo se troppo lungo (limiti API)
        max_chars = 12000  # ~3000 tokens
        if len(text) > max_chars:
            self.logger.info(f"  Troncamento testo: {len(text)} -> {max_chars} caratteri")
            text = text[:max_chars] + "..."
        
        if analysis_type == 'full':
            return self._full_analysis(text, parsed_doc)
        elif analysis_type == 'summary':
            return self._generate_summary(text)
        elif analysis_type == 'topics':
            return self._extract_topics(text)
        elif analysis_type == 'insights':
            return self._extract_insights(text)
        else:
            raise ValueError(f"Tipo analisi non supportato: {analysis_type}")
    
    def _full_analysis(self, text: str, parsed_doc: Dict) -> Dict:
        """Analisi completa del documento"""
        
        self.logger.info(f"🤖 Analisi AI completa: {parsed_doc['filename']}")
        
        prompt = f"""Analizza questo documento di consulenza aziendale e fornisci un'analisi strutturata.

DOCUMENTO:
{text}

Fornisci l'analisi in formato JSON con questa struttura:
{{
    "summary": "Riassunto esecutivo del documento (200-300 parole)",
    "topics": ["Lista", "di", "topic", "rilevanti"],
    "key_insights": [
        "Insight 1 - punto chiave o finding importante",
        "Insight 2 - altro punto chiave",
        "Insight 3 - ...",
    ],
    "technologies": ["Tecnologie", "menzionate"],
    "trends": ["Trend", "identificati"],
    "business_implications": "Implicazioni per il business (100 parole)",
    "sentiment": "positive/neutral/negative",
    "confidence": "high/medium/low"
}}

IMPORTANTE:
- Rispondi SOLO con JSON valido
- Estrai insights concreti e specifici
- Identifica tecnologie emergenti menzionate
- I topics devono essere categorie ampie (AI, Blockchain, Cloud, Cybersecurity, etc.)
"""
        
        try:
            response = self._call_llm(prompt)
            
            # Parse JSON response
            result = self._parse_json_response(response)
            
            if result:
                # Aggiungi metadata
                result['analyzed_at'] = datetime.now().isoformat()
                result['model'] = self.model
                result['provider'] = self.provider
                result['source_document'] = parsed_doc['filename']
                
                self.logger.info(f"  ✅ Analisi completata: {len(result.get('key_insights', []))} insights estratti")
                
                return result
            else:
                self.logger.error("❌ Risposta AI non valida")
                return None
        
        except Exception as e:
            self.logger.error(f"❌ Errore analisi AI: {e}")
            return None
    
    def _generate_summary(self, text: str) -> str:
        """Genera solo summary"""
        
        prompt = f"""Fornisci un riassunto esecutivo conciso (200-250 parole) di questo documento:

{text}

Riassunto:"""
        
        return self._call_llm(prompt)
    
    def _extract_topics(self, text: str) -> List[str]:
        """Estrae solo topics"""
        
        prompt = f"""Analizza questo testo e identifica i topic principali (max 5).
Scegli tra questi topic standard:
- Artificial Intelligence
- Machine Learning
- Quantum Computing
- Blockchain
- Cloud Computing
- Cybersecurity
- IoT
- Data Analytics
- Digital Transformation
- Automation
- Metaverse
- ESG/Sustainability
- 5G
- Edge Computing

TESTO:
{text}

Rispondi SOLO con la lista di topic separati da virgola:"""
        
        response = self._call_llm(prompt)
        
        # Parse topics
        topics = [t.strip() for t in response.split(',')]
        return topics
    
    def _extract_insights(self, text: str) -> List[str]:
        """Estrae solo key insights"""
        
        prompt = f"""Estrai i 5 key insights più importanti da questo documento.
Ogni insight deve essere:
- Concreto e specifico
- Actionable per il business
- Basato su dati/fatti nel documento

DOCUMENTO:
{text}

Rispondi con lista numerata:
1."""
        
        response = self._call_llm(prompt)
        
        # Parse insights
        insights = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Rimuovi numero iniziale
                insight = re.sub(r'^[\d\-\.\)]+\s*', '', line)
                if insight:
                    insights.append(insight)
        
        return insights
    
    def _call_llm(self, prompt: str, max_tokens: int = 2000) -> str:
        """Chiama LLM (OpenAI o Anthropic)"""
        
        if self.provider == 'openai':
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Sei un esperto analista di documenti di consulenza aziendale. Fornisci analisi dettagliate e strutturate."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )
            return response.choices[0].message.content
        
        elif self.provider == 'anthropic':
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
    
    @staticmethod
    def _parse_json_response(response: str) -> Optional[Dict]:
        """Parse JSON da risposta LLM"""
        
        # Trova blocco JSON
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        
        if json_match:
            json_str = json_match.group()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Prova a parsare tutta la risposta
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return None
    
    def batch_analyze(self, parsed_docs: List[Dict]) -> List[Dict]:
        """
        Analizza batch di documenti
        
        Args:
            parsed_docs: Lista di documenti parsati
        
        Returns:
            Lista di analisi
        """
        analyses = []
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"🤖 Batch AI Analysis: {len(parsed_docs)} documenti")
        self.logger.info(f"{'='*80}\n")
        
        for i, doc in enumerate(parsed_docs, 1):
            self.logger.info(f"[{i}/{len(parsed_docs)}] Analyzing: {doc['filename']}")
            
            analysis = self.analyze_document(doc, 'full')
            
            if analysis:
                analyses.append(analysis)
        
        self.logger.info(f"\n✅ Analisi completate: {len(analyses)}/{len(parsed_docs)}")
        
        return analyses


# Fallback analyzer senza AI (basato su keywords)
class KeywordAnalyzer:
    """Analyzer semplice basato su keywords (quando AI non disponibile)"""
    
    def __init__(self):
        self.logger = utils.logger
        
        # Keywords per topic
        self.topic_keywords = {
            'AI': ['artificial intelligence', 'ai', 'machine learning', 'ml', 'deep learning', 
                   'neural network', 'nlp', 'computer vision'],
            'Quantum': ['quantum', 'qubit', 'quantum computing'],
            'Blockchain': ['blockchain', 'crypto', 'web3', 'defi', 'nft', 'distributed ledger'],
            'Cloud': ['cloud', 'aws', 'azure', 'gcp', 'saas', 'paas', 'iaas'],
            'Cybersecurity': ['cyber', 'security', 'hack', 'threat', 'breach', 'encryption'],
            'IoT': ['iot', 'internet of things', 'sensor', 'connected device'],
            'Data Analytics': ['data', 'analytics', 'big data', 'business intelligence', 'bi'],
            'Digital Transformation': ['digital transformation', 'digitalization', 'digital'],
            'Automation': ['automation', 'rpa', 'robotic process'],
            'ESG': ['esg', 'sustainability', 'climate', 'green', 'carbon'],
            '5G': ['5g', 'fifth generation'],
            'Metaverse': ['metaverse', 'virtual reality', 'vr', 'ar', 'augmented reality']
        }
    
    def analyze_document(self, parsed_doc: Dict) -> Dict:
        """Analisi basata su keywords"""
        
        text = parsed_doc.get('text', '').lower()
        
        # Estrai topics
        topics = []
        for topic, keywords in self.topic_keywords.items():
            if any(kw in text for kw in keywords):
                topics.append(topic)
        
        # Summary semplice (prime N parole)
        words = parsed_doc.get('text', '').split()
        summary = ' '.join(words[:200]) + '...'
        
        return {
            'summary': summary,
            'topics': topics or ['Technology'],
            'key_insights': ['Documento analizzato con keyword extraction'],
            'technologies': [],
            'trends': [],
            'business_implications': 'Richiede analisi AI per insights dettagliati',
            'sentiment': 'neutral',
            'confidence': 'low',
            'analyzed_at': datetime.now().isoformat(),
            'model': 'keyword_extraction',
            'provider': 'local',
            'source_document': parsed_doc['filename']
        }
