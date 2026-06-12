"""Verificacao visual do redesign: screenshots desktop e mobile de cada pagina.

Somente leitura: loga, navega e fotografa. Nao salva palpite nem placar.
"""
import os
import sys

from playwright.sync_api import sync_playwright

URL = "http://localhost:8501"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verification_screenshots")
DESKTOP = {"width": 1280, "height": 800}
MOBILE = {"width": 390, "height": 844}

USERNAME = os.environ["COPA_USER"]
PASSWORD = os.environ["COPA_PASS"]

PAGES = [
    ("Fase de Grupos", "grupos"),
    ("Mata-Mata", "matamata"),
    ("Ranking", "ranking"),
    ("Painel Admin", "admin"),
]


def shot(page, name):
    page.screenshot(path=os.path.join(OUT, f"{name}.png"), full_page=True)
    print(f"  screenshot: {name}.png")


def main():
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport=DESKTOP)
        page.goto(URL)
        page.wait_for_timeout(6000)

        shot(page, "00_login_desktop")
        page.set_viewport_size(MOBILE)
        page.wait_for_timeout(1500)
        shot(page, "00_login_mobile")
        page.set_viewport_size(DESKTOP)
        page.wait_for_timeout(1500)

        # Login (form da aba Entrar = primeiro stForm da pagina)
        form = page.locator('[data-testid="stForm"]').first
        form.get_by_label("Nome de usuario", exact=True).fill(USERNAME)
        form.get_by_label("Senha", exact=True).fill(PASSWORD)
        form.locator('[data-testid="stBaseButton-primaryFormSubmit"]').click()
        try:
            page.wait_for_selector('[data-testid="stSidebar"]', timeout=45000)
            page.wait_for_timeout(4000)
        except Exception:
            print("ERRO: login falhou (sidebar nao apareceu)")
            shot(page, "99_login_failed")
            browser.close()
            sys.exit(1)
        print("login OK")

        for label, slug in PAGES:
            btn = page.locator(f'[data-testid="stSidebar"] button:has-text("{label}")')
            if btn.count() == 0:
                print(f"  AVISO: botao '{label}' nao encontrado, pulando")
                continue
            btn.first.click()
            page.wait_for_timeout(5000)
            shot(page, f"{slug}_desktop")
            page.set_viewport_size(MOBILE)
            page.wait_for_timeout(2000)
            shot(page, f"{slug}_mobile")
            page.set_viewport_size(DESKTOP)
            page.wait_for_timeout(2000)

        browser.close()
    print("verificacao concluida")


if __name__ == "__main__":
    main()
