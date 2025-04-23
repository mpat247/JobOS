# scraper/discovery/utils/page_scraper.py

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def scrape_page_structured(url: str) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=30000, wait_until='load')
        except Exception as e:
            browser.close()
            return {"error": f"Failed to load page: {str(e)}"}

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # Extract main elements
    page_title = soup.title.string if soup.title else ""
    headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]
    paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
    links = [
        {"text": a.get_text(strip=True), "href": a.get('href')}
        for a in soup.find_all('a', href=True)
    ]
    buttons = [btn.get_text(strip=True) for btn in soup.find_all('button')]

    return {
        "url": url,
        "title": page_title,
        "headings": headings,
        "paragraphs": paragraphs,
        "links": links,
        "buttons": buttons
    }
