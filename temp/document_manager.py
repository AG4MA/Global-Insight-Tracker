# -*- coding: utf-8 -*-
"""
Document Manager - Sistema per scaricare, salvare e gestire documenti
Salva PDF, DOCX con metadata e sistema di deduplicazione

Autore: Senior Python Developer
Data: 22 Dicembre 2025
"""

import os
import hashlib
import json
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path
import requests
import utils


class DocumentManager:
    """Gestisce download e storage dei documenti"""
    
    def __init__(self, storage_dir: str = None):
        """
        Args:
            storage_dir: Directory dove salvare i documenti
        """
        if storage_dir is None:
            storage_dir = os.path.join(os.path.dirname(__file__), 'documents')
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Directory per metadata
        self.metadata_dir = self.storage_dir / 'metadata'
        self.metadata_dir.mkdir(exist_ok=True)
        
        # File per tracciare documenti scaricati (evitare duplicati)
        self.index_file = self.metadata_dir / 'document_index.json'
        self.index = self._load_index()
        
        self.logger = utils.logger
    
    def _load_index(self) -> Dict:
        """Carica indice dei documenti"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_index(self):
        """Salva indice"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False, default=str)
    
    def download_document(self, report: Dict) -> Optional[str]:
        """
        Scarica documento e salva con metadata
        
        Args:
            report: Dizionario con info report (da crawler)
        
        Returns:
            Path al file scaricato o None
        """
        document_url = report.get('document_url')
        
        if not document_url:
            self.logger.warning(f"⚠️  Nessun URL documento per: {report['title'][:50]}")
            return None
        
        # Controlla se già scaricato usando hash URL
        url_hash = self._hash_string(document_url)
        
        if url_hash in self.index:
            self.logger.info(f"📄 Documento già esistente: {self.index[url_hash]['filename']}")
            return self.index[url_hash]['filepath']
        
        # Scarica documento
        self.logger.info(f"⬇️  Downloading: {document_url}")
        
        try:
            response = requests.get(
                document_url,
                timeout=30,
                headers={'User-Agent': utils.get_random_user_agent()}
            )
            response.raise_for_status()
            
            # Determina estensione
            content_type = response.headers.get('content-type', '').lower()
            
            if 'pdf' in content_type or document_url.endswith('.pdf'):
                extension = '.pdf'
            elif 'word' in content_type or document_url.endswith(('.docx', '.doc')):
                extension = '.docx'
            else:
                # Prova a indovinare dal content
                if response.content[:4] == b'%PDF':
                    extension = '.pdf'
                else:
                    extension = '.pdf'  # Default
            
            # Genera nome file sicuro
            safe_title = self._sanitize_filename(report['title'])
            source = report.get('source', 'unknown').lower()
            timestamp = datetime.now().strftime('%Y%m%d')
            
            filename = f"{source}_{timestamp}_{safe_title[:50]}{extension}"
            filepath = self.storage_dir / filename
            
            # Salva file
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            self.logger.info(f"✅ Saved: {filename} ({file_size} bytes)")
            
            # Salva metadata
            metadata = {
                'url_hash': url_hash,
                'filename': filename,
                'filepath': str(filepath),
                'document_url': document_url,
                'source': report.get('source'),
                'title': report['title'],
                'topics': report.get('topics', []),
                'download_date': datetime.now().isoformat(),
                'file_size': file_size,
                'content_type': content_type,
                'report_url': report.get('url'),
                'description': report.get('description', '')
            }
            
            # Aggiungi a index
            self.index[url_hash] = metadata
            self._save_index()
            
            # Salva metadata individuale
            metadata_file = self.metadata_dir / f"{filename}.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return str(filepath)
        
        except Exception as e:
            self.logger.error(f"❌ Errore download {document_url}: {e}")
            return None
    
    def batch_download(self, reports: List[Dict]) -> List[str]:
        """
        Scarica batch di documenti
        
        Args:
            reports: Lista di report da scaricare
        
        Returns:
            Lista di filepath scaricati
        """
        downloaded = []
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"📦 Inizio batch download: {len(reports)} documenti")
        self.logger.info(f"{'='*80}\n")
        
        for i, report in enumerate(reports, 1):
            self.logger.info(f"[{i}/{len(reports)}] {report['title'][:60]}")
            
            filepath = self.download_document(report)
            
            if filepath:
                downloaded.append(filepath)
        
        self.logger.info(f"\n✅ Download completati: {len(downloaded)}/{len(reports)}")
        
        return downloaded
    
    def get_documents_by_topic(self, topic: str) -> List[Dict]:
        """
        Ottieni tutti i documenti per un dato topic
        
        Args:
            topic: Nome del topic (es. 'AI', 'Blockchain')
        
        Returns:
            Lista di metadata documenti
        """
        matching_docs = []
        
        for url_hash, metadata in self.index.items():
            topics = metadata.get('topics', [])
            if topic in topics:
                matching_docs.append(metadata)
        
        return matching_docs
    
    def get_all_documents(self) -> List[Dict]:
        """Ottieni lista di tutti i documenti"""
        return list(self.index.values())
    
    def get_all_topics(self) -> List[str]:
        """Ottieni lista di tutti i topic trovati"""
        topics = set()
        
        for metadata in self.index.values():
            topics.update(metadata.get('topics', []))
        
        return sorted(list(topics))
    
    @staticmethod
    def _hash_string(text: str) -> str:
        """Crea hash MD5 di una stringa"""
        return hashlib.md5(text.encode()).hexdigest()
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Rende un filename sicuro per filesystem"""
        # Rimuovi caratteri non validi
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Rimuovi spazi multipli
        filename = ' '.join(filename.split())
        
        # Sostituisci spazi con underscore
        filename = filename.replace(' ', '_')
        
        return filename
