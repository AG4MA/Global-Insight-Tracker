# -*- coding: utf-8 -*-
"""BCG Scraper"""

from typing import Dict, List
from ..core.config import SOURCES
from .selenium_scraper import SeleniumScraper


class BCGScraper(SeleniumScraper):
    """Scraper specializzato per BCG Publications"""
    
    def __init__(self):
        super().__init__(SOURCES['bcg'])
