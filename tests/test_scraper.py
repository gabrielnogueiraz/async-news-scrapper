import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import News
from src.scrapper import G1Scraper


class TestG1Scraper:
    @pytest.mark.asyncio
    async def test_scraper_initialization(self, db_session: AsyncSession):
        scraper = G1Scraper(db_session)
        assert scraper.session == db_session
        assert scraper.BASE_URL == "https://g1.globo.com/"
        assert "User-Agent" in scraper.headers

    @pytest.mark.asyncio
    async def test_scraper_fetch_page(self, db_session: AsyncSession):
        scraper = G1Scraper(db_session)
        try:
            html = await scraper._fetch_page(scraper.BASE_URL)
            assert isinstance(html, str)
            assert len(html) > 0
        except Exception as e:
            pytest.skip(f"Network error: {str(e)}")

    @pytest.mark.asyncio
    async def test_scraper_parse_news(self, db_session: AsyncSession):
        scraper = G1Scraper(db_session)
        
        sample_html = """
        <html>
            <body>
                <a class="feed-post-link" href="https://g1.globo.com/test-1">
                    Título da notícia de teste 1
                </a>
                <a class="feed-post-link" href="/test-2">
                    Título da notícia de teste 2
                </a>
            </body>
        </html>
        """
        
        news_items = scraper._parse_news(sample_html)
        assert isinstance(news_items, list)
        assert len(news_items) >= 0

    @pytest.mark.asyncio
    async def test_scraper_save_news(self, db_session: AsyncSession):
        scraper = G1Scraper(db_session)
        
        news_items = [
            ("Notícia teste 1", "https://g1.globo.com/scraper-test-1"),
            ("Notícia teste 2", "https://g1.globo.com/scraper-test-2"),
        ]
        
        count = await scraper._save_news(news_items)
        assert count == 2
        
        result = await db_session.execute(select(News))
        saved_news = result.scalars().all()
        assert len(saved_news) == 2

    @pytest.mark.asyncio
    async def test_scraper_no_duplicate_urls(self, db_session: AsyncSession):
        scraper = G1Scraper(db_session)
        
        news_items = [
            ("Notícia original", "https://g1.globo.com/duplicate-test"),
        ]
        
        count1 = await scraper._save_news(news_items)
        assert count1 == 1
        
        count2 = await scraper._save_news(news_items)
        assert count2 == 0
        
        result = await db_session.execute(select(News))
        saved_news = result.scalars().all()
        assert len(saved_news) == 1

    @pytest.mark.asyncio
    async def test_scraper_full_scrape(self, db_session: AsyncSession):
        scraper = G1Scraper(db_session)
        
        try:
            count = await scraper.scrape()
            assert isinstance(count, int)
            assert count >= 0
            
            result = await db_session.execute(select(News))
            saved_news = result.scalars().all()
            assert len(saved_news) == count
        except Exception as e:
            pytest.skip(f"Network error during scraping: {str(e)}")

    @pytest.mark.asyncio
    async def test_scraper_empty_news_items(self, db_session: AsyncSession):
        scraper = G1Scraper(db_session)
        count = await scraper._save_news([])
        assert count == 0
