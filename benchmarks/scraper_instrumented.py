"""
Instrumented version of the scraper for benchmarking.
"""
import asyncio
import time
from typing import List, Tuple

import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urljoin

from src.models import News
from benchmarks.metrics import MetricsCollector


class InstrumentedG1Scraper:
    """G1 Scraper with instrumentation for performance metrics."""
    
    BASE_URL = "https://g1.globo.com/"
    TIMEOUT = aiohttp.ClientTimeout(total=30, connect=10)
    MAX_RETRIES = 3
    RETRY_DELAY = 2

    def __init__(self, session: AsyncSession, collector: MetricsCollector):
        self.session = session
        self.collector = collector
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    async def _fetch_page(self, url: str) -> str:
        """Fetch page with metrics collection."""
        start_time = time.perf_counter()
        success = False
        error = None
        result = ""
        
        for attempt in range(self.MAX_RETRIES):
            try:
                async with aiohttp.ClientSession(timeout=self.TIMEOUT) as client:
                    async with client.get(url, headers=self.headers) as response:
                        response.raise_for_status()
                        result = await response.text()
                        success = True
                        break
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                error = str(e)
                if attempt == self.MAX_RETRIES - 1:
                    raise Exception(f"Failed to fetch {url} after {self.MAX_RETRIES} attempts: {str(e)}")
                await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
        
        end_time = time.perf_counter()
        self.collector.record_request(url, start_time, end_time, success, error)
        
        return result

    def _parse_news(self, html: str) -> List[Tuple[str, str]]:
        """Parse news from HTML (no instrumentation needed - CPU bound)."""
        soup = BeautifulSoup(html, "html.parser")
        news_items = []

        selectors = [
            {"class": "feed-post-link"},
            {"class": "bastian-feed-item"},
            {"class": "feed-media-wrapper"},
        ]

        for selector in selectors:
            links = soup.find_all("a", selector)
            for link in links:
                title = link.get_text(strip=True)
                href = link.get("href", "")

                if not title or not href or len(title) < 10:
                    continue

                full_url = urljoin(self.BASE_URL, href) if not href.startswith("http") else href

                if "g1.globo.com" in full_url and title not in [item[0] for item in news_items]:
                    news_items.append((title, full_url))

        return news_items

    async def _save_news(self, news_items: List[Tuple[str, str]]) -> int:
        """Save news to database."""
        if not news_items:
            return 0

        existing_urls = await self.session.execute(
            select(News.url).where(News.url.in_([url for _, url in news_items]))
        )
        existing_urls_set = {row[0] for row in existing_urls.fetchall()}

        new_items = [
            {"title": title, "url": url}
            for title, url in news_items
            if url not in existing_urls_set
        ]

        if not new_items:
            return 0

        stmt = insert(News).values(new_items)
        stmt = stmt.on_conflict_do_nothing(index_elements=["url"])

        await self.session.execute(stmt)
        await self.session.commit()

        return len(new_items)

    async def scrape(self) -> Tuple[int, int]:
        """
        Scrape news and return metrics.
        
        Returns:
            Tuple of (news_scraped, news_saved)
        """
        html = await self._fetch_page(self.BASE_URL)
        news_items = self._parse_news(html)
        news_saved = await self._save_news(news_items)
        
        return len(news_items), news_saved
