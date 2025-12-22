"""Test Selenium per Deloitte"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

opts = Options()
opts.add_argument('--headless')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-gpu')
opts.add_argument('--disable-dev-shm-usage')

print("Avvio Chrome...")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=opts)

print("Carico pagina Deloitte...")
driver.get('https://www2.deloitte.com/it/it/pages/technology/topics/insights.html')
time.sleep(5)

html = driver.page_source
print(f'HTML: {len(html)} bytes')

# Cerca elementi promo
promo_els = driver.find_elements(By.CSS_SELECTOR, 'div.promo')
print(f'div.promo: {len(promo_els)}')

# Cerca link insights
cards = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/insights/"]')
print(f'Link insights: {len(cards)}')

# Trova tutti i titoli h3/h4
titles = driver.find_elements(By.CSS_SELECTOR, 'h3, h4')
print(f'Titoli h3/h4: {len(titles)}')
for t in titles[:10]:
    txt = t.text.strip()
    if txt:
        print(f'  - {txt[:60]}')

driver.quit()
print("Test completato!")
