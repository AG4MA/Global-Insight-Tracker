# -*- coding: utf-8 -*-
"""
ESEMPIO SEMPLIFICATO - Big4 Watchdog
Questo script dimostra la logica core del sistema in modo semplificato
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

print("\n" + "="*80)
print("📚 ESEMPIO SEMPLIFICATO - Come Funziona Big4 Watchdog")
print("="*80 + "\n")

# ==============================================================================
# STEP 1: CONFIGURAZIONE
# ==============================================================================
print("STEP 1: Configurazione")
print("-"*80)

# URL target di esempio (Deloitte Insights)
URL = "https://www2.deloitte.com/us/en/insights.html"
print(f"URL Target: {URL}")

# Selettori CSS per estrarre dati (questi sono esempi - devono essere verificati)
SELECTORS = {
    'article_container': 'div.cmp-card',
    'title': 'h3.cmp-card__title',
    'link': 'a.cmp-card__link',
    'date': 'time',
    'description': 'p.cmp-card__description'
}
print(f"Selettori configurati: {len(SELECTORS)}\n")

# ==============================================================================
# STEP 2: RICHIESTA HTTP
# ==============================================================================
print("STEP 2: Richiesta HTTP")
print("-"*80)

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"Invio richiesta GET a {URL[:50]}...")
    response = requests.get(URL, headers=headers, timeout=30)
    print(f"✅ Risposta ricevuta: Status {response.status_code}")
    print(f"   Dimensione HTML: {len(response.text):,} caratteri\n")

except Exception as e:
    print(f"❌ Errore: {e}")
    exit(1)

# ==============================================================================
# STEP 3: PARSING HTML
# ==============================================================================
print("STEP 3: Parsing HTML con BeautifulSoup")
print("-"*80)

soup = BeautifulSoup(response.text, 'lxml')
print(f"✅ HTML parsato con successo")
print(f"   Tag trovati: {len(soup.find_all())}\n")

# ==============================================================================
# STEP 4: ESTRAZIONE ARTICOLI
# ==============================================================================
print("STEP 4: Estrazione Articoli")
print("-"*80)

# Trova containers degli articoli
containers = soup.select(SELECTORS['article_container'])
print(f"📦 Trovati {len(containers)} containers di articoli")

if len(containers) == 0:
    print("⚠️  ATTENZIONE: Nessun container trovato!")
    print("   Il selettore CSS potrebbe essere obsoleto.")
    print("   Apri il sito nel browser, premi F12, e identifica il selettore corretto.\n")
    
    # Mostra alcuni div come esempio
    print("   Primi 5 div trovati nella pagina:")
    for i, div in enumerate(soup.find_all('div')[:5], 1):
        classes = div.get('class', [])
        print(f"   {i}. <div class='{' '.join(classes)}'> ...")
    
    print("\n💡 Suggerimento: Cerca div che contiene gli articoli e usa la sua classe")
    print("   Esempio: Se vedi <div class='insight-card'>, usa 'div.insight-card'\n")

# Estrai dati da ogni container
articles = []
for idx, container in enumerate(containers[:5], 1):  # Limita a 5 per esempio
    try:
        # Estrai titolo
        title_elem = container.select_one(SELECTORS['title'])
        title = title_elem.get_text(strip=True) if title_elem else "N/A"
        
        # Estrai link
        link_elem = container.select_one(SELECTORS['link'])
        link = link_elem.get('href') if link_elem else "N/A"
        
        # Estrai data
        date_elem = container.select_one(SELECTORS['date'])
        date = date_elem.get_text(strip=True) if date_elem else "N/A"
        
        # Estrai descrizione
        desc_elem = container.select_one(SELECTORS['description'])
        description = desc_elem.get_text(strip=True) if desc_elem else "N/A"
        
        # Aggiungi a lista
        articles.append({
            'Titolo': title[:60] + "..." if len(title) > 60 else title,
            'Data': date,
            'Link': link,
            'Descrizione': description[:80] + "..." if len(description) > 80 else description
        })
        
        print(f"  ✓ Articolo {idx}: {title[:50]}...")
    
    except Exception as e:
        print(f"  ✗ Articolo {idx}: Errore - {e}")

print(f"\n✅ Estratti {len(articles)} articoli\n")

# ==============================================================================
# STEP 5: CREAZIONE DATAFRAME
# ==============================================================================
print("STEP 5: Creazione DataFrame Pandas")
print("-"*80)

if articles:
    df = pd.DataFrame(articles)
    print(f"✅ DataFrame creato: {len(df)} righe × {len(df.columns)} colonne")
    print("\nPreview dei dati:")
    print(df.to_string(index=False, max_colwidth=40))
else:
    print("⚠️  Nessun articolo da processare")
    df = pd.DataFrame()

print()

# ==============================================================================
# STEP 6: EXPORT EXCEL (opzionale)
# ==============================================================================
print("STEP 6: Export Excel (Opzionale)")
print("-"*80)

if not df.empty:
    try:
        output_file = 'output/esempio_scraping.xlsx'
        df.to_excel(output_file, index=False, sheet_name='Articoli')
        print(f"✅ File Excel salvato: {output_file}")
        print(f"   Aprilo per vedere i risultati!\n")
    except Exception as e:
        print(f"⚠️  Non posso creare Excel: {e}")
        print("   (Probabilmente manca openpyxl: pip install openpyxl)\n")
else:
    print("⚠️  Nessun dato da esportare\n")

# ==============================================================================
# RIEPILOGO
# ==============================================================================
print("="*80)
print("📊 RIEPILOGO ESEMPIO")
print("="*80)
print(f"""
Questo è un esempio semplificato che dimostra i 6 passaggi chiave:

1. ✅ Configurazione URL e selettori CSS
2. ✅ Richiesta HTTP con headers appropriati
3. ✅ Parsing HTML con BeautifulSoup
4. ✅ Estrazione dati con selettori CSS
5. ✅ Creazione DataFrame Pandas
6. ✅ Export su Excel

Il sistema completo (main.py) implementa:
- ✨ Scraping di 6 società diverse
- ✨ Retry logic e gestione errori
- ✨ Deduplicazione e validazione
- ✨ Append mode per non sovrascrivere dati
- ✨ Logging dettagliato
- ✨ Filtri per tematiche rilevanti
- ✨ Support per Selenium (siti dinamici)

IMPORTANTE: I selettori CSS in questo esempio potrebbero non funzionare
perché i siti cambiano struttura HTML. Verifica sempre con F12 nel browser!

Per usare il sistema completo:
    python main.py --companies deloitte --max-articles 3
""")
print("="*80 + "\n")

# ==============================================================================
# DEBUG INFO
# ==============================================================================
if len(containers) == 0:
    print("🔍 MODALITÀ DEBUG")
    print("="*80)
    print("Se non hai trovato articoli, ecco come procedere:\n")
    print("1. Apri nel browser: " + URL)
    print("2. Premi F12 (Developer Tools)")
    print("3. Trova un articolo visivamente")
    print("4. Click destro → Inspect Element")
    print("5. Guarda il tag HTML:")
    print("   <div class='QUESTO-E-IL-SELETTORE'>")
    print("      <h3>Titolo Articolo</h3>")
    print("   </div>")
    print("\n6. Aggiorna SELECTORS in questo script:")
    print("   SELECTORS = {")
    print("       'article_container': 'div.QUESTO-E-IL-SELETTORE',")
    print("       'title': 'h3',  # o h2, etc.")
    print("       ...")
    print("   }")
    print("\n7. Riesegui questo script\n")
    print("="*80 + "\n")
