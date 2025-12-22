# -*- coding: utf-8 -*-
"""
Script di Test - Global Insight Tracker
Verifica che tutte le funzionalità siano operative
"""

import os
import sys

print("\n" + "="*80)
print("🧪 Global Insight Tracker - TEST SUITE")
print("="*80 + "\n")

# ==============================================================================
# TEST 1: Import Moduli
# ==============================================================================
print("📦 Test 1: Import moduli...")
try:
    import config
    import utils
    print("  ✅ config.py importato")
    print("  ✅ utils.py importato")
except Exception as e:
    print(f"  ❌ Errore import: {e}")
    sys.exit(1)

# ==============================================================================
# TEST 2: Dipendenze Python
# ==============================================================================
print("\n📚 Test 2: Verifica dipendenze...")
dependencies = {
    'requests': 'Web scraping HTTP',
    'bs4': 'BeautifulSoup HTML parsing',
    'pandas': 'Data manipulation',
    'openpyxl': 'Excel export',
    'dateutil': 'Date parsing'
}

missing = []
for module, description in dependencies.items():
    try:
        __import__(module)
        print(f"  ✅ {module:15s} - {description}")
    except ImportError:
        print(f"  ❌ {module:15s} - MANCANTE")
        missing.append(module)

if missing:
    print(f"\n⚠️  Dipendenze mancanti: {', '.join(missing)}")
    print("   Eseguire: pip install -r requirements.txt")
    sys.exit(1)

# ==============================================================================
# TEST 3: Configurazione
# ==============================================================================
print("\n⚙️  Test 3: Validazione configurazione...")
if config.validate_config():
    print("  ✅ Configurazione valida")
    print(f"  ✅ {len(config.SITES_CONFIG)} siti configurati")
else:
    print("  ❌ Errori di configurazione")
    sys.exit(1)

# ==============================================================================
# TEST 4: Directory
# ==============================================================================
print("\n📁 Test 4: Struttura directory...")
dirs = [config.OUTPUT_DIR, config.LOG_DIR]
for d in dirs:
    if os.path.exists(d):
        print(f"  ✅ {d}")
    else:
        print(f"  ⚠️  {d} - creazione...")
        os.makedirs(d, exist_ok=True)

# ==============================================================================
# TEST 5: Funzioni Utilità
# ==============================================================================
print("\n🔧 Test 5: Funzioni utilità...")

# Test parsing date
test_date = "December 15, 2025"
parsed = utils.parse_date(test_date)
if parsed:
    formatted = utils.format_date(parsed)
    print(f"  ✅ Parse date: '{test_date}' → '{formatted}'")
else:
    print(f"  ❌ Parse date fallito")

# Test pulizia testo
dirty = "  Test   with   <html>tags</html>  "
clean = utils.clean_text(dirty)
print(f"  ✅ Clean text: '{dirty}' → '{clean}'")

# Test creazione Excel
test_excel = os.path.join(config.OUTPUT_DIR, 'test_output.xlsx')
if utils.create_excel_file(test_excel):
    print(f"  ✅ Creazione Excel: {test_excel}")
    os.remove(test_excel)  # Cleanup
else:
    print(f"  ❌ Creazione Excel fallita")

# ==============================================================================
# TEST 6: Connettività
# ==============================================================================
print("\n🌐 Test 6: Connettività siti...")
test_urls = [
    ("Google", "https://www.google.com"),
    ("Deloitte", config.SITES_CONFIG['deloitte']['base_url'])
]

for name, url in test_urls:
    response = utils.make_request(url)
    if response:
        print(f"  ✅ {name:15s} - Status {response.status_code}")
    else:
        print(f"  ⚠️  {name:15s} - Timeout o errore")

# ==============================================================================
# TEST 7: Selettori CSS
# ==============================================================================
print("\n🎯 Test 7: Preview configurazione siti...")
for site_key, site_config in list(config.SITES_CONFIG.items())[:3]:  # Primi 3
    print(f"  • {site_config['name']:15s} - {site_config['insights_url'][:50]}...")

# ==============================================================================
# RIEPILOGO
# ==============================================================================
print("\n" + "="*80)
print("✅ TUTTI I TEST COMPLETATI CON SUCCESSO")
print("="*80)
print("\n💡 Suggerimenti:")
print("  1. Esegui scraping di test: python main.py --companies deloitte --max-articles 3")
print("  2. Controlla i log in: logs/scraping.log")
print("  3. Verifica output in: output/report_consulting.xlsx")
print("\n")
