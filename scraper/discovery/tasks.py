# discovery/tasks.py

from celery import shared_task
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
import logging
from logging_config import setup_logging
from urllib.parse import quote_plus

logger = setup_logging()

@shared_task
def search_normalize_task(company: str, country: str) -> list:
    """
    DuckDuckGo ► playwright ► top-5 URLs / query ► normalize ► dedupe.

    • Keeps the same signature & return type as before.
    • Only the scraping block changed:
        – Uses the proper SERP URL (`?t=h_&q=…&ia=web`, url-encoded).
        – Pulls links via the stable selector 
          `article[data-testid="result"] h2 a` (matches the HTML you pasted).
        – Collects up to 5 links per query, skipping ads/redirects.
    """
    logger.info(
        "[search_normalize_task] Starting task for company=%s, country=%s",
        company,
        country,
    )

    queries = [
        f"{company} careers {country}",
        f"{company} job openings {country}",
        f"{company} hiring page {country}",
    ]

    raw_urls: list[str] = []

    # ── helper: canonicalize host/path ───────────────────────────
    def normalize_url(u: str) -> str:
        try:
            p = urlparse(u)
            host = p.netloc.replace("www.", "")
            path = p.path.rstrip("/")
            return urlunparse((p.scheme, host, path, "", "", ""))
        except Exception as exc:  # noqa: BLE001
            logger.warning("[normalize_url] Failed (%s): %s", exc, u)
            return u

    # ── Playwright scrape loop ──────────────────────────────────
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for q in queries:
            encoded = quote_plus(q)
            ddg_url = f"https://duckduckgo.com/?t=h_&q={encoded}&ia=web"

            try:
                logger.debug("[search_normalize_task] GET %s", ddg_url)
                page.goto(ddg_url, wait_until="domcontentloaded", timeout=30_000)

                # Wait until at least one organic result shows up
                page.wait_for_selector('article[data-testid="result"]', timeout=10_000)

                # Grab the first 5 result anchors
                anchors = page.locator('article[data-testid="result"] h2 a').all()[:5]

                for a in anchors:
                    href = a.get_attribute("href")
                    if href and href.startswith(("http://", "https://")):
                        logger.debug("[search_normalize_task] href=%s", href)
                        raw_urls.append(href)

                # Optional HTML snapshot for debugging
                page_content = page.content()
                fname = f"debug_{encoded[:50]}.html"
                with open(fname, "w", encoding="utf-8") as fh:
                    fh.write(page_content)

            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "[search_normalize_task] Error while querying '%s': %s", q, exc
                )

        browser.close()

    # ── dedupe / normalize ──────────────────────────────────────
    normalized = list({normalize_url(u) for u in raw_urls})
    logger.info(
        "[search_normalize_task] %d unique URLs for %s (%s)",
        len(normalized),
        company,
        country,
    )
    logger.debug("[search_normalize_task] URLs=%s", normalized)
    return normalized


@shared_task
def crawl_career_pages_task(normalized_urls: list, company: str, country: str):
    """
    Placeholder for Stage 2.
    Right now it just logs and echoes the normalized URLs.
    Later you’ll replace this with your BFS crawler.
    """
    logger.info(f"[crawl_career_pages_task] Starting task for company: {company}, country: {country}")
    logger.debug(f"[crawl_career_pages_task] URLs: {normalized_urls}")
    return normalized_urls
