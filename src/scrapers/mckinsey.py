# -*- coding: utf-8 -*-
"""McKinsey Scraper"""

from typing import Dict, List
from ..core.config import SOURCES
from .selenium_scraper import SeleniumScraper


class McKinseyScraper(SeleniumScraper):
    """Scraper specializzato per McKinsey Insights"""
    
    def __init__(self):
        super().__init__(SOURCES['mckinsey'])
