# -*- coding: utf-8 -*-
"""
AI Analyzer - Analisi contenuti con AI
"""

from typing import Dict, List, Optional
from ..core.config import AI
from ..core.utils import logger


class AIAnalyzer:
    """
    Analizzatore AI per contenuti
    
    Supporta OpenAI e Anthropic (opzionale).
    """
    
    def __init__(self):
        self.enabled = AI.enabled and (AI.openai_api_key or AI.anthropic_api_key)
        self._client = None
    
    def analyze(self, text: str, prompt: str = None) -> Optional[str]:
        """
        Analizza testo con AI
        
        Args:
            text: Testo da analizzare
            prompt: Prompt custom
            
        Returns:
            Analisi o None
        """
        if not self.enabled:
            logger.debug("AI analysis disabled")
            return None
        
        if prompt is None:
            prompt = (
                "Analizza questo articolo e fornisci: "
                "1) Tema principale, 2) Key insights, 3) Implicazioni business"
            )
        
        try:
            return self._call_api(text, prompt)
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return None
    
    def _call_api(self, text: str, prompt: str) -> str:
        """Chiama API AI"""
        if AI.openai_api_key:
            return self._call_openai(text, prompt)
        elif AI.anthropic_api_key:
            return self._call_anthropic(text, prompt)
        return ''
    
    def _call_openai(self, text: str, prompt: str) -> str:
        """Chiama OpenAI API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=AI.openai_api_key)
            
            response = client.chat.completions.create(
                model=AI.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text[:4000]}
                ],
                max_tokens=AI.max_tokens
            )
            return response.choices[0].message.content
        except ImportError:
            logger.error("openai package not installed")
            return ''
    
    def _call_anthropic(self, text: str, prompt: str) -> str:
        """Chiama Anthropic API"""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=AI.anthropic_api_key)
            
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=AI.max_tokens,
                messages=[
                    {"role": "user", "content": f"{prompt}\n\n{text[:4000]}"}
                ]
            )
            return response.content[0].text
        except ImportError:
            logger.error("anthropic package not installed")
            return ''
    
    def summarize(self, articles: List[Dict]) -> str:
        """
        Genera sommario di multipli articoli
        
        Args:
            articles: Lista articoli
            
        Returns:
            Sommario aggregato
        """
        if not self.enabled or not articles:
            return ''
        
        # Prepara testo
        text_parts = []
        for art in articles[:10]:
            text_parts.append(f"- {art.get('title', '')}: {art.get('description', '')}")
        
        combined = "\n".join(text_parts)
        
        prompt = (
            "Sei un analista di tecnologie emergenti. "
            "Riassumi questi articoli identificando: "
            "1) Trend principali, 2) Tecnologie chiave, 3) Outlook generale"
        )
        
        return self.analyze(combined, prompt) or ''
