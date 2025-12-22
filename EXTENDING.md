# 📖 GUIDA: Come Aggiungere Nuove Società di Consulenza

## Esempio: Aggiungere Bain & Company

### Step 1: Identifica gli URL Target

Vai sul sito web e trova la sezione "Insights":
- URL Base: `https://www.bain.com`
- Insights: `https://www.bain.com/insights/`

### Step 2: Ispeziona la Struttura HTML

1. Apri la pagina Insights nel browser
2. Premi F12 per aprire Developer Tools
3. Clicca con destro su un articolo → "Inspect Element"
4. Identifica i selettori CSS:

```html
<!-- Esempio struttura HTML di Bain -->
<div class="insight-card">
    <a href="/insights/article-123">
        <h3 class="insight-title">Titolo Articolo</h3>
    </a>
    <span class="insight-date">Dec 20, 2025</span>
    <span class="insight-topic">Technology</span>
    <p class="insight-description">Descrizione breve...</p>
</div>
```

### Step 3: Aggiungi Configurazione in `config.py`

Apri `config.py` e aggiungi nel dizionario `SITES_CONFIG`:

```python
# In config.py, dentro SITES_CONFIG
'bain': {
    'name': 'Bain & Company',
    'base_url': 'https://www.bain.com',
    'insights_url': 'https://www.bain.com/insights/',
    'alternative_urls': [
        'https://www.bain.com/insights/topics/technology/',
        'https://www.bain.com/insights/topics/digital/'
    ],
    'selectors': {
        # Usa i selettori che hai identificato
        'article_container': 'div.insight-card, article.article-item',
        'title': 'h3.insight-title, h2.article-title',
        'link': 'a.insight-link',
        'date': 'span.insight-date, time',
        'category': 'span.insight-topic, a.topic-tag',
        'description': 'p.insight-description, div.summary'
    },
    'date_format': '%b %d, %Y',  # es. "Dec 20, 2025"
    'requires_selenium': False  # True se carica articoli con AJAX
},
```

### Step 4: Aggiorna CLI in `main.py`

Nel file `main.py`, trova la sezione `parse_arguments()` e aggiungi 'bain':

```python
parser.add_argument(
    '--companies',
    nargs='+',
    choices=['deloitte', 'pwc', 'ey', 'kpmg', 'mckinsey', 'bcg', 'bain'],  # <-- Aggiungi qui
    help='Specifica quali società scrapare (default: tutte)'
)
```

### Step 5: Test

```bash
# Test solo Bain
python main.py --companies bain --max-articles 3 --verbose
```

### Step 6: Debug Selettori (se necessario)

Se non trova articoli:

1. Controlla il log: `logs/scraping.log`
2. Verifica selettore usato vs HTML reale
3. Prova selettori alternativi separati da virgola:

```python
'article_container': 'div.insight-card, article.content-card, div.article',
```

---

## Template Completo per Nuova Società

```python
'COMPANY_KEY': {
    'name': 'Nome Completo',
    'base_url': 'https://www.example.com',
    'insights_url': 'https://www.example.com/insights',
    'alternative_urls': [
        'https://www.example.com/insights/topic1',
        'https://www.example.com/insights/topic2'
    ],
    'selectors': {
        'article_container': 'div.article-card',  # Obbligatorio
        'title': 'h3.title, h2.heading',          # Obbligatorio
        'link': 'a.article-link',                 # Obbligatorio
        'date': 'time, span.date',                # Opzionale
        'category': 'span.topic',                 # Opzionale
        'description': 'p.description'            # Opzionale
    },
    'date_format': '%B %d, %Y',
    'requires_selenium': False
},
```

---

## Selettori CSS: Cheat Sheet

### Selettori Base
```css
div.classname          /* Elemento con classe */
#id                    /* Elemento con ID */
article.card           /* Tag + classe */
```

### Selettori Multipli (usa virgola)
```python
'title': 'h3.title, h2.heading, a.link-title'
# Prova h3.title, se non esiste h2.heading, poi a.link-title
```

### Selettori Discendenti
```css
div.card h3            /* h3 dentro div.card */
article > h2           /* h2 figlio diretto di article */
```

### Attributi
```css
a[href*="insights"]    /* Link con "insights" nell'href */
time[datetime]         /* Tag time con attributo datetime */
```

---

## Formati Data Comuni

```python
'%B %d, %Y'      # December 20, 2025
'%d %B %Y'       # 20 December 2025
'%b %d, %Y'      # Dec 20, 2025
'%d %b %Y'       # 20 Dec 2025
'%Y-%m-%d'       # 2025-12-20
'%d/%m/%Y'       # 20/12/2025
'%m/%d/%Y'       # 12/20/2025
'%B %Y'          # December 2025
```

---

## Quando Usare Selenium

Abilita `requires_selenium: True` se:

✅ Gli articoli si caricano con scroll infinito  
✅ Vedi "Loading..." quando apri la pagina  
✅ In DevTools vedi chiamate AJAX/XHR  
✅ Il contenuto HTML è generato da JavaScript  

---

## Test Veloce per Nuova Società

```python
# Crea file test_new_site.py
import requests
from bs4 import BeautifulSoup

url = 'https://www.bain.com/insights/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

# Test selettori
containers = soup.select('div.insight-card')
print(f"Trovati {len(containers)} articoli")

for container in containers[:3]:
    title = container.select_one('h3.insight-title')
    print(f"  - {title.get_text(strip=True) if title else 'NO TITLE'}")
```

---

## Checklist Post-Aggiunta

- [ ] Configurazione aggiunta in `SITES_CONFIG`
- [ ] Selettori testati con script veloce
- [ ] Aggiunta nei `choices` del CLI
- [ ] Test scraping: `python main.py --companies NUOVA --max-articles 2`
- [ ] Verifica Excel generato
- [ ] Aggiorna README con nuova società

---

**Suggerimento**: Mantieni un file `sites_research.md` con appunti su:
- URL validi per ogni società
- Struttura HTML osservata
- Frequenza aggiornamento contenuti
- Note su blocchi anti-bot

---

## Esempio Completo: Accenture

```python
'accenture': {
    'name': 'Accenture',
    'base_url': 'https://www.accenture.com',
    'insights_url': 'https://www.accenture.com/us-en/insights',
    'alternative_urls': [
        'https://www.accenture.com/us-en/insights/technology',
        'https://www.accenture.com/us-en/insights/artificial-intelligence-summary'
    ],
    'selectors': {
        'article_container': 'div.cmp-teaser, article.content-card',
        'title': 'h3.cmp-teaser__title, h2.title',
        'link': 'a.cmp-teaser__link',
        'date': 'time, span.date',
        'category': 'span.topic, p.eyebrow',
        'description': 'p.cmp-teaser__description'
    },
    'date_format': '%B %d, %Y',
    'requires_selenium': False
},
```

Poi nel CLI:
```python
choices=['deloitte', 'pwc', 'ey', 'kpmg', 'mckinsey', 'bcg', 'accenture'],
```

Test:
```bash
python main.py --companies accenture --max-articles 5
```

---

**Nota**: Alcuni siti bloccano bot aggressivamente. Se hai `403 Forbidden`:
1. Aumenta `REQUEST_DELAY` a 5-10 secondi
2. Usa `requires_selenium: True`
3. Aggiungi proxy rotation (avanzato)

Buona estensione! 🚀
