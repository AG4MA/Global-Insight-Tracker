# -*- coding: utf-8 -*-
"""Deloitte Scraper"""

from typing import Dict, List
from ..core.config import SOURCES
from .selenium_scraper import SeleniumScraper


class DeloitteScraper(SeleniumScraper):
    """Scraper specializzato per Deloitte Insights"""
    
    def __init__(self):
        super().__init__(SOURCES['deloitte'])
