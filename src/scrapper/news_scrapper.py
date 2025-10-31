import asyncio
from typing import List, Tuple
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import News


class G1Scraper:
    BASE_URL = "https://g1.globo.com/"
    TIMEOUT = aiohttp.ClientTimeout(total=30, connect=10)
    MAX_RETRIES = 3
    RETRY_DELAY = 2

    def __init__(self, session: AsyncSession):
        self.session = session
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    async def _fetch_page(self, url: str) -> str:
        for attempt in range(self.MAX_RETRIES):
            try:
                async with aiohttp.ClientSession(timeout=self.TIMEOUT) as client:
                    async with client.get(url, headers=self.headers) as response:
                        response.raise_for_status()
                        return await response.text()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == self.MAX_RETRIES - 1:
                    raise Exception(f"Failed to fetch {url} after {self.MAX_RETRIES} attempts: {str(e)}")
                await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
        return ""

    def _parse_news(self, html: str) -> List[Tuple[str, str]]:
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

    async def scrape(self) -> int:
        html = await self._fetch_page(self.BASE_URL)
        news_items = self._parse_news(html)
        return await self._save_news(news_items)
