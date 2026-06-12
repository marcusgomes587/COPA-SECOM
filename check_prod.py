"""Checa se a versao nova esta no ar: procura marcador do CSS novo na pagina."""
from playwright.sync_api import sync_playwright

URL = "https://copa-secom-3ymwcweyz5wwujfbjlc7za.streamlit.app/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    page.goto(URL, timeout=60000)
    page.wait_for_timeout(12000)
    content = page.content()
    page.screenshot(path="verification_screenshots/prod_login.png", full_page=True)
    if "Zzzz" in content or "wake" in content.lower():
        print("APP DORMINDO: precisa acordar (botao de wake up)")
    print("CSS novo (cardIn):", "SIM" if "cardIn" in content else "NAO")
    print("CSS novo (craque-badge):", "SIM" if "craque-badge" in content else "NAO")
    browser.close()
