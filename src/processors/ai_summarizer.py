# -*- coding: utf-8 -*-
"""
AI Summarizer - Riassume documenti con OpenAI
"""

import os
import json
from typing import Dict, List, Optional
from pathlib import Path

from ..core.config import OUTPUT_DIR
from ..core.utils import logger


# Cache per riassunti
SUMMARIES_CACHE = OUTPUT_DIR / "summaries_cache.json"


class AISummarizer:
    """
    Riassume documenti usando OpenAI GPT.
    
    Features:
    - Riassunto singolo documento
    - Riassunto aggregato per topic
    - Caching per evitare chiamate duplicate
    """
    
    def __init__(self, api_key: str = None):
        """
        Inizializza summarizer.
        
        Args:
            api_key: OpenAI API key. Se None, cerca in env OPENAI_API_KEY
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY', '')
        self.client = None
        self.cache = self._load_cache()
        self.model = "gpt-4o-mini"  # Economico e veloce
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            logger.warning("⚠️ OpenAI API key non configurata - riassunti disabilitati")
    
    def _init_client(self):
        """Inizializza client OpenAI"""
        if self.client is None and self.enabled:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                logger.error("❌ openai non installato - pip install openai")
                self.enabled = False
    
    def summarize_document(self, article: Dict) -> Dict:
        """
        Riassume un singolo documento.
        
        Args:
            article: Dict con 'content_text', 'title', 'source'
            
        Returns:
            Article con 'summary' aggiunto
        """
        if not self.enabled:
            return article
        
        url = article.get('url', '')
        
        # Check cache
        if url in self.cache:
            article['summary'] = self.cache[url]
            return article
        
        content = article.get('content_text', '')
        title = article.get('title', '')
        source = article.get('source', '')
        
        if not content or len(content) < 100:
            article['summary'] = ''
            return article
        
        try:
            self._init_client()
            
            # Tronca contenuto se troppo lungo
            max_chars = 12000  # ~3000 tokens
            if len(content) > max_chars:
                content = content[:max_chars] + "..."
            
            prompt = f"""Sei un analista esperto di tecnologie e business. 
Riassumi questo articolo di {source} in italiano in modo chiaro e conciso.

TITOLO: {title}

CONTENUTO:
{content}

Fornisci:
1. **Tema principale** (1 frase)
2. **Punti chiave** (3-5 bullet points)
3. **Implicazioni per il business** (2-3 frasi)

Rispondi in italiano, max 300 parole."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Sei un analista di tecnologie emergenti."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content
            article['summary'] = summary
            
            # Salva in cache
            self.cache[url] = summary
            self._save_cache()
            
            logger.info(f"✓ Summarized: {title[:40]}...")
            
        except Exception as e:
            logger.warning(f"✗ Summary failed: {e}")
            article['summary'] = ''
        
        return article
    
    def summarize_all(self, articles: List[Dict], max_summaries: int = 30) -> List[Dict]:
        """
        Riassume tutti gli articoli.
        
        Args:
            articles: Lista articoli con content_text
            max_summaries: Limite per costi API
            
        Returns:
            Articoli con summary
        """
        if not self.enabled:
            logger.warning("⚠️ AI Summarizer disabilitato")
            return articles
        
        logger.info(f"🤖 Generazione riassunti (max {max_summaries})...")
        
        count = 0
        for article in articles:
            if count >= max_summaries:
                break
            
            # Skip se già ha summary in cache
            if article.get('url') in self.cache:
                article['summary'] = self.cache[article['url']]
                continue
            
            # Skip se no content
            if not article.get('content_text'):
                continue
            
            self.summarize_document(article)
            count += 1
        
        logger.info(f"✅ Riassunti generati: {count}")
        return articles
    
    def generate_topic_recap(self, topic: str, articles: List[Dict]) -> str:
        """
        Genera recap aggregato per un topic.
        
        Combina i riassunti di tutti gli articoli di un topic
        per creare una visione d'insieme del "pensiero" delle company.
        
        Args:
            topic: Nome del topic
            articles: Articoli del topic (con summary)
            
        Returns:
            Recap aggregato
        """
        if not self.enabled or not articles:
            return ''
        
        # Raccogli riassunti per source
        summaries_by_source = {}
        for art in articles:
            source = art.get('source', 'Unknown')
            summary = art.get('summary', '')
            title = art.get('title', '')
            
            if summary:
                if source not in summaries_by_source:
                    summaries_by_source[source] = []
                summaries_by_source[source].append(f"- {title}: {summary[:300]}")
        
        if not summaries_by_source:
            return ''
        
        # Prepara input per GPT
        input_text = f"TOPIC: {topic}\n\n"
        for source, summaries in summaries_by_source.items():
            input_text += f"=== {source} ===\n"
            input_text += "\n".join(summaries[:3])  # Max 3 per source
            input_text += "\n\n"
        
        try:
            self._init_client()
            
            prompt = f"""Analizza questi riassunti di articoli sul tema "{topic}" 
pubblicati da diverse società di consulenza.

{input_text}

Genera un RECAP AGGREGATO in italiano che:
1. Identifica i TREND COMUNI tra le diverse company
2. Evidenzia le DIFFERENZE di prospettiva
3. Fornisce un OUTLOOK generale sul tema

Max 400 parole. Usa un tono professionale e analitico."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Sei un senior analyst che sintetizza report di consulenza."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.4
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.warning(f"Topic recap failed: {e}")
            return ''
    
    def generate_all_recaps(self, topic_groups: Dict[str, List]) -> Dict[str, str]:
        """
        Genera recap per tutti i topic.
        
        Args:
            topic_groups: Dict topic -> lista articoli
            
        Returns:
            Dict topic -> recap
        """
        recaps = {}
        
        for topic, articles in topic_groups.items():
            if len(articles) >= 2:  # Almeno 2 articoli per recap
                recap = self.generate_topic_recap(topic, articles)
                if recap:
                    recaps[topic] = recap
                    logger.info(f"✓ Recap: {topic}")
        
        return recaps
    
    def _load_cache(self) -> Dict:
        """Carica cache da file"""
        if SUMMARIES_CACHE.exists():
            try:
                with open(SUMMARIES_CACHE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_cache(self):
        """Salva cache su file"""
        try:
            with open(SUMMARIES_CACHE, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.debug(f"Cache save failed: {e}")
