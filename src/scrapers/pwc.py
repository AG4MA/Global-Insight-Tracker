# -*- coding: utf-8 -*-
"""PwC Scraper"""

from typing import Dict, List
from ..core.config import SOURCES
from .selenium_scraper import SeleniumScraper


class PwCScraper(SeleniumScraper):
    """Scraper specializzato per PwC Insights"""
    
    def __init__(self):
        super().__init__(SOURCES['pwc'])
