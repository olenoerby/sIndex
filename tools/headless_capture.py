import os
from playwright.sync_api import sync_playwright

os.makedirs('screenshots', exist_ok=True)
url = 'http://127.0.0.1:8000/list.html'
print('Capturing', url)
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width':1280,'height':800})
    page.goto(url, wait_until='networkidle')
    page.screenshot(path='screenshots/list.png', full_page=True)
    print('Saved screenshots/list.png')
    browser.close()
