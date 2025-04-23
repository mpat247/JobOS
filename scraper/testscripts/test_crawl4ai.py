#!/usr/bin/env python3
import sys
import asyncio
import textwrap
import requests
from typing import List, Tuple, Optional
from urllib.parse import urlparse, urljoin, urlencode

from lxml import html
from sentence_transformers import SentenceTransformer, util
import torch

from duckduckgo_search import DDGS
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.filters import FilterChain, DomainFilter, URLPatternFilter
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

# ─── CONFIG ─────────────────────────────────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral-7b-instruct"

# ─── 1️⃣ Helpers ─────────────────────────────────────────────────────────────────
def getCompanyHomepage(companyName: str) -> str:
    domain = companyName.lower().replace(" ", "")
    url = f"https://www.{domain}.com"
    print(f"🔧 Trying homepage: {url}")
    try:
        resp = requests.head(url, timeout=5)
        if resp.status_code < 400 and "html" in resp.headers.get("Content-Type", ""):
            print(f"✅ Found live homepage: {url}")
            return url
    except Exception:
        pass
    print(f"⚠️  Could not verify homepage; using {url} anyway")
    return url

def getFirstCareerUrl(companyName: str) -> Optional[str]:
    query = f"{companyName} careers site"
    print(f"🔍 DuckDuckGo search for: {query}")
    with DDGS() as ddgs:
        for res in ddgs.text(keywords=query, max_results=1):
            href = res.get("href")
            print(f"🎯 Got career URL candidate: {href}")
            return href
    print("❌ DuckDuckGo returned no results")
    return None

def chunkText(text: str, maxChars: int = 2000) -> List[str]:
    return list(textwrap.wrap(text, maxChars, break_long_words=False))

def isJobListingsPage(chunk: str) -> bool:
    prompt = (
        "You are a classifier. Answer ONLY 'YES' or 'NO':\n"
        "“Does this chunk show multiple job postings (cards/titles/locations)?”\n\n"
        f"```html\n{chunk}\n```"
    )
    payload = {
        "model":       OLLAMA_MODEL,
        "prompt":      prompt,
        "temperature": 0.0,
        "max_tokens":  16,
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=20)
        resp.raise_for_status()
        answer = resp.json().get("response", "").strip().upper()
        print(f"   🤖 Ollama answered: {answer}")
        return answer.startswith("Y")
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return False

def detectSearchForm(tree: html.HtmlElement) -> Optional[html.HtmlElement]:
    for form in tree.xpath("//form"):
        inputs = form.xpath(".//input")
        for inp in inputs:
            attrs = (inp.attrib.get("type","")+inp.attrib.get("name","")+inp.attrib.get("placeholder","")).lower()
            if "search" in attrs:
                return form
    return None

def constructSearchUrl(baseUrl: str, form: html.HtmlElement) -> str:
    action = form.attrib.get("action", "")
    searchUrl = urljoin(baseUrl, action)
    inputs = form.xpath(".//input")
    param = "q"
    for inp in inputs:
        if "search" in (inp.attrib.get("type","")+inp.attrib.get("name","")+inp.attrib.get("placeholder","")).lower():
            param = inp.attrib.get("name", param)
            break
    return f"{searchUrl}?{urlencode({param: ''})}"

# ─── 2️⃣ Crawl & Chunk Collection ────────────────────────────────────────────────
async def crawlAndCollectTextChunks(startUrl: str) -> List[Tuple[str,str]]:
    parsedDomain = urlparse(startUrl).netloc
    print(f"🌐 Deep‑crawling under domain: {parsedDomain}")

    urlPatterns = ["*careers*", "*jobs*", "*vacancies*", "*openings*", "*search-results*"]
    filterChain = FilterChain([
        URLPatternFilter(patterns=urlPatterns),
        DomainFilter(allowed_domains=[parsedDomain])
    ])
    scorer = KeywordRelevanceScorer(
        keywords=["career","jobs","vacancies","open positions","job listings"],
        weight=0.7
    )
    strategy = BestFirstCrawlingStrategy(
        max_depth=3,
        include_external=False,
        filter_chain=filterChain,
        url_scorer=scorer,
        max_pages=50
    )
    config = CrawlerRunConfig(
        deep_crawl_strategy=strategy,
        scraping_strategy=LXMLWebScrapingStrategy(),
        stream=False,
        verbose=False
    )

    chunksWithUrls: List[Tuple[str,str]] = []
    async with AsyncWebCrawler() as crawler:
        try:
            results = await crawler.arun(startUrl, config=config)
            async for res in results:
                text = res.cleaned_text or res.markdown or res.raw_html or ""
                for chunk in chunkText(text):
                    chunksWithUrls.append((chunk, res.url))
            print(f"🔖 Collected {len(chunksWithUrls)} text chunks")
        except Exception as e:
            print("❌ Crawl error:", e)
    return chunksWithUrls

# ─── 3️⃣ Build & Query Embedding Index ──────────────────────────────────────────
def buildEmbeddingIndex(chunksWithUrls: List[Tuple[str,str]]):
    print("⏳ Building semantic index …")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [c for c,_ in chunksWithUrls]
    embeddings = model.encode(texts, convert_to_tensor=True, show_progress_bar=False)
    print("✅ Embedding index ready")
    return embeddings, model

def queryChunks(embeddings: torch.Tensor, model, query: str, topK: int = 10) -> List[int]:
    qEmb = model.encode(query, convert_to_tensor=True)
    scores = util.cos_sim(qEmb, embeddings)[0]
    topIdxs = torch.topk(scores, k=topK).indices.tolist()
    print(f"🎯 Top {topK} chunk indices for “{query}”: {topIdxs}")
    return topIdxs

# ─── 4️⃣ Verify or Follow Search Form ────────────────────────────────────────────
def verifyOrFollowSearch(url: str) -> Optional[str]:
    print(f"   🔍 Verifying page content at: {url}")
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        # direct chunk classification
        for chunk in chunkText(resp.text):
            if isJobListingsPage(chunk):
                return url

        # detect + follow search form
        tree = html.fromstring(resp.text)
        form = detectSearchForm(tree)
        if form:
            searchUrl = constructSearchUrl(resp.url, form)
            print(f"   🔗 Found search form; querying at {searchUrl}")
            resp2 = requests.get(searchUrl, timeout=10)
            resp2.raise_for_status()
            for chunk in chunkText(resp2.text):
                if isJobListingsPage(chunk):
                    return searchUrl
    except Exception:
        pass
    return None

# ─── 5️⃣ Full RAG‑Driven Finder ─────────────────────────────────────────────────
async def findJobListingsPageRAG(company: str) -> Optional[str]:
    # determine start URL
    if company.startswith("http"):
        startUrl = company
    else:
        careerUrl = getFirstCareerUrl(company)
        startUrl = careerUrl or getCompanyHomepage(company)

    print(f"🚀 Starting RAG crawl from: {startUrl}")
    chunksWithUrls = await crawlAndCollectTextChunks(startUrl)
    if not chunksWithUrls:
        return None

    embeddings, embedModel = buildEmbeddingIndex(chunksWithUrls)
    topIdxs = queryChunks(embeddings, embedModel, "job listings page", topK=10)

    # collect unique candidate URLs
    seen = set()
    candidates = []
    for idx in topIdxs:
        url = chunksWithUrls[idx][1]
        if url not in seen:
            seen.add(url)
            candidates.append(url)
    print("🔍 Candidate URLs to verify:", candidates)

    for candidate in candidates:
        result = verifyOrFollowSearch(candidate)
        if result:
            return result
    return None

# ─── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print("Usage: python find_job_listings.py <CompanyName or URL>")
        sys.exit(1)

    company = " ".join(sys.argv[1:])
    print(f"🎯 Target company/input: {company}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    found = loop.run_until_complete(findJobListingsPageRAG(company))

    if found:
        print(f"\n✅ Job listings page found: {found}")
    else:
        print("\n❌ No job listings page could be identified.")

if __name__ == "__main__":
    main()
