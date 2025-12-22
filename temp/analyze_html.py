# -*- coding: utf-8 -*-
"""Script per analizzare la struttura HTML dei siti"""

from bs4 import BeautifulSoup
import re

def analyze_deloitte():
    with open('c:/projects/Global-Insight-Tracker/temp_deloitte.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    print("=" * 80)
    print("ANALISI STRUTTURA DELOITTE")
    print("=" * 80)
    
    # Cerca tutte le classi uniche
    all_classes = set()
    for tag in soup.find_all(True, class_=True):
        for c in tag.get('class', []):
            if any(kw in c.lower() for kw in ['promo', 'card', 'item', 'teaser', 'article', 'feature', 'content']):
                all_classes.add(c)
    
    print("\n📦 CLASSI RILEVANTI TROVATE:")
    for c in sorted(all_classes):
        print(f"  • {c}")
    
    # Cerca pattern specifici
    patterns = [
        'div.promo-content',
        'div[class*="promo"]',
        'div[class*="card"]',
        'article',
        'div[class*="teaser"]',
        'div[class*="item"]',
    ]
    
    print("\n🔍 RICERCA CONTENITORI ARTICOLI:")
    
    # Promo containers
    promos = soup.find_all('div', class_=re.compile(r'promo', re.I))
    print(f"\n  div con 'promo' in class: {len(promos)}")
    for p in promos[:3]:
        link = p.find('a', href=True)
        title = p.find(['h1','h2','h3','h4','h5','span'])
        if link and title:
            print(f"    • {title.get_text(strip=True)[:50]}")
            print(f"      {link.get('href', '')[:60]}")
    
    # Featured
    featured = soup.find_all('div', class_=re.compile(r'featured|hero', re.I))
    print(f"\n  div con 'featured/hero' in class: {len(featured)}")
    
    # Content blocks
    content = soup.find_all('div', class_=re.compile(r'content-block|content-item', re.I))
    print(f"\n  div con 'content-block/item' in class: {len(content)}")
    
    # Cerca link con titoli lunghi fuori dai menu
    print("\n📰 ARTICOLI PROBABILI (link con titoli > 30 char, fuori menu):")
    seen = set()
    for a in soup.find_all('a', href=True):
        href = a.get('href', '')
        if '/insights/' not in href or '.html' not in href:
            continue
        if 'icid=disidenav' in href:  # Skip navigation
            continue
        
        text = a.get_text(strip=True)
        if len(text) > 30 and href not in seen:
            seen.add(href)
            parent = a.find_parent(['div', 'section'])
            parent_class = parent.get('class', []) if parent else []
            print(f"\n  📄 {text[:60]}")
            print(f"     URL: {href[:70]}")
            print(f"     Parent class: {parent_class}")

if __name__ == '__main__':
    analyze_deloitte()
