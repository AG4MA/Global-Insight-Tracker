# -*- coding: utf-8 -*-
"""
Test Scrapers
"""

import pytest
import sys
from pathlib import Path

# Aggiungi root al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import SOURCES
from src.core.utils import normalize_url, clean_text, extract_category_from_url
from src.analyzers.topic_classifier import TopicClassifier


class TestUtils:
    """Test utility functions"""
    
    def test_clean_text(self):
        assert clean_text("  hello  world  ") == "hello world"
        assert clean_text("") == ""
        assert len(clean_text("x" * 1000, max_length=100)) <= 100
    
    def test_normalize_url(self):
        assert normalize_url("/path", "https://example.com") == "https://example.com/path"
        assert normalize_url("https://other.com/page", "") == "https://other.com/page"
    
    def test_extract_category(self):
        assert extract_category_from_url("/insights/ai-trends") == "Artificial Intelligence"
        assert extract_category_from_url("/cloud-computing") == "Cloud Computing"
        assert extract_category_from_url("/random-page") == "General"


class TestTopicClassifier:
    """Test topic classifier"""
    
    def test_classify_ai(self):
        classifier = TopicClassifier()
        article = {
            'title': 'The Future of Artificial Intelligence',
            'description': 'Machine learning trends'
        }
        topic = classifier.classify(article)
        assert topic in ['Artificial Intelligence', 'Generative AI']
    
    def test_classify_cloud(self):
        classifier = TopicClassifier()
        article = {
            'title': 'Cloud Migration Strategies',
            'description': 'AWS and Azure deployment'
        }
        assert classifier.classify(article) == 'Cloud Computing'
    
    def test_group_by_topic(self):
        classifier = TopicClassifier()
        articles = [
            {'title': 'AI Article', 'topic': 'AI'},
            {'title': 'Cloud Article', 'topic': 'Cloud'},
            {'title': 'Another AI', 'topic': 'AI'},
        ]
        groups = classifier.group_by_topic(articles)
        assert len(groups['AI']) == 2
        assert len(groups['Cloud']) == 1


class TestConfig:
    """Test configuration"""
    
    def test_sources_defined(self):
        assert 'deloitte' in SOURCES
        assert 'mckinsey' in SOURCES
        assert 'bcg' in SOURCES
    
    def test_source_has_required_fields(self):
        for key, source in SOURCES.items():
            assert source.name
            assert source.base_url
            assert source.insights_url
            assert source.link_pattern


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
