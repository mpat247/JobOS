import asyncio
from crawl4ai import AsyncWebCrawler
from helpers.job_board_detector import detect_job_board

async def main():
    target_url = "https://jobs.lever.co/gohighlevel"

    # Initialize crawler
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=target_url)

        # Extract markdown + raw HTML
        markdown = result.markdown
        html = result.html  # fallback for pattern matching

        # Detect job board type
        job_board = detect_job_board(url=target_url, page_content=html)

        # Output results
        print(f"\n🕸️ URL: {target_url}")
        print(f"📌 Job board type: {job_board}")
        print(f"\n📝 Markdown extracted:\n{markdown}")  
if __name__ == "__main__":
    asyncio.run(main())
