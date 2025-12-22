# -*- coding: utf-8 -*-
"""
Excel Generator - Generazione report Excel
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd

from ..core.config import OUTPUT_DIR, OUTPUT
from ..core.utils import logger


class ExcelGenerator:
    """
    Generatore report Excel
    
    Crea e aggiorna file Excel con articoli estratti.
    """
    
    def __init__(self, filename: str = None):
        """
        Inizializza generator
        
        Args:
            filename: Nome file output (default da config)
        """
        if filename is None:
            filename = OUTPUT.excel_filename
        
        self.filepath = OUTPUT_DIR / filename
    
    def save(self, articles: List[Dict], append: bool = True) -> bool:
        """
        Salva articoli su Excel
        
        Args:
            articles: Lista articoli
            append: Se True, aggiunge a file esistente
            
        Returns:
            True se successo
        """
        if not articles:
            logger.warning("Nessun articolo da salvare")
            return False
        
        try:
            # Converti a DataFrame
            df_new = pd.DataFrame(articles)
            
            # Aggiungi timestamp
            df_new['scraped_at'] = datetime.now().isoformat()
            
            # Carica esistente se append
            if append and self.filepath.exists():
                try:
                    df_existing = pd.read_excel(self.filepath)
                    df = pd.concat([df_existing, df_new], ignore_index=True)
                    
                    # Rimuovi duplicati per URL
                    df = df.drop_duplicates(subset=['url'], keep='last')
                    
                    logger.info(f"Aggiunti {len(df_new)} record (totale: {len(df)})")
                except Exception as e:
                    logger.warning(f"Errore lettura esistente: {e}")
                    df = df_new
            else:
                df = df_new
            
            # Ordina colonne
            columns_order = [
                'title', 'source', 'category', 'topic', 
                'description', 'url', 'date', 'scraped_at'
            ]
            cols = [c for c in columns_order if c in df.columns]
            cols += [c for c in df.columns if c not in cols]
            df = df[cols]
            
            # Salva
            df.to_excel(self.filepath, index=False, engine='openpyxl')
            logger.info(f"✅ Salvato: {self.filepath}")
            
            return True
            
        except Exception as e:
            logger.error(f"Errore salvataggio Excel: {e}")
            return False
    
    def load(self) -> pd.DataFrame:
        """
        Carica articoli da Excel
        
        Returns:
            DataFrame con articoli
        """
        if not self.filepath.exists():
            return pd.DataFrame()
        
        try:
            return pd.read_excel(self.filepath)
        except Exception as e:
            logger.error(f"Errore lettura Excel: {e}")
            return pd.DataFrame()
    
    def get_stats(self) -> Dict:
        """
        Statistiche file Excel
        
        Returns:
            Dict con statistiche
        """
        df = self.load()
        
        if df.empty:
            return {'total': 0, 'sources': {}, 'topics': {}}
        
        return {
            'total': len(df),
            'sources': df['source'].value_counts().to_dict() if 'source' in df else {},
            'topics': df['topic'].value_counts().to_dict() if 'topic' in df else {},
        }
