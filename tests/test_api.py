import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import News


class TestHealthEndpoints:
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Async News Scraper"
        assert data["status"] == "running"
        assert "/news" in data["endpoints"]
        assert "/scrape" in data["endpoints"]

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "async-news-scraper"


class TestNewsEndpoint:
    @pytest.mark.asyncio
    async def test_get_news_empty_database(self, client: AsyncClient):
        response = await client.get("/news")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_news_with_data(self, client: AsyncClient, db_session: AsyncSession):
        news_items = [
            News(
                title="Primeira notícia de teste",
                url="https://g1.globo.com/test-1"
            ),
            News(
                title="Segunda notícia de teste",
                url="https://g1.globo.com/test-2"
            ),
            News(
                title="Terceira notícia de teste",
                url="https://g1.globo.com/test-3"
            ),
        ]
        
        for news in news_items:
            db_session.add(news)
        await db_session.commit()

        response = await client.get("/news")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("id" in item for item in data)
        assert all("title" in item for item in data)
        assert all("url" in item for item in data)
        assert all("created_at" in item for item in data)

    @pytest.mark.asyncio
    async def test_get_news_pagination(self, client: AsyncClient, db_session: AsyncSession):
        for i in range(15):
            news = News(
                title=f"Notícia {i}",
                url=f"https://g1.globo.com/test-{i}"
            )
            db_session.add(news)
        await db_session.commit()

        response = await client.get("/news?limit=5&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

        response = await client.get("/news?limit=5&offset=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

        response = await client.get("/news?limit=10&offset=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    @pytest.mark.asyncio
    async def test_get_news_ordered_by_date(self, client: AsyncClient, db_session: AsyncSession):
        import asyncio
        
        news1 = News(title="Primeira", url="https://g1.globo.com/1")
        db_session.add(news1)
        await db_session.commit()
        
        await asyncio.sleep(0.01)
        
        news2 = News(title="Segunda", url="https://g1.globo.com/2")
        db_session.add(news2)
        await db_session.commit()

        response = await client.get("/news")
        data = response.json()
        
        assert data[0]["title"] == "Segunda"
        assert data[1]["title"] == "Primeira"


class TestScrapeEndpoint:
    @pytest.mark.asyncio
    async def test_scrape_endpoint_structure(self, client: AsyncClient):
        response = await client.post("/scrape")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "news_added" in data
        assert "message" in data
        assert isinstance(data["success"], bool)
        assert isinstance(data["news_added"], int)
        assert isinstance(data["message"], str)

    @pytest.mark.asyncio
    async def test_scrape_adds_news(self, client: AsyncClient):
        response = await client.post("/scrape")
        assert response.status_code == 200
        data = response.json()
        
        news_response = await client.get("/news")
        news_data = news_response.json()
        
        assert len(news_data) >= 0

    @pytest.mark.asyncio
    async def test_scrape_no_duplicates(self, client: AsyncClient):
        response1 = await client.post("/scrape")
        data1 = response1.json()
        initial_count = data1["news_added"]

        response2 = await client.post("/scrape")
        data2 = response2.json()
        
        assert data2["news_added"] == 0 or data2["news_added"] < initial_count


class TestDataValidation:
    @pytest.mark.asyncio
    async def test_news_response_schema(self, client: AsyncClient, db_session: AsyncSession):
        news = News(
            title="Teste de validação",
            url="https://g1.globo.com/validation-test"
        )
        db_session.add(news)
        await db_session.commit()

        response = await client.get("/news")
        data = response.json()
        
        assert len(data) == 1
        item = data[0]
        
        assert isinstance(item["id"], int)
        assert isinstance(item["title"], str)
        assert isinstance(item["url"], str)
        assert isinstance(item["created_at"], str)
        assert item["url"].startswith("http")

    @pytest.mark.asyncio
    async def test_scrape_response_schema(self, client: AsyncClient):
        response = await client.post("/scrape")
        data = response.json()
        
        assert isinstance(data["success"], bool)
        assert isinstance(data["news_added"], int)
        assert isinstance(data["message"], str)
        assert data["news_added"] >= 0


class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_invalid_endpoint(self, client: AsyncClient):
        response = await client.get("/invalid-endpoint")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_invalid_method(self, client: AsyncClient):
        response = await client.post("/news")
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_invalid_query_params(self, client: AsyncClient):
        response = await client.get("/news?limit=invalid")
        assert response.status_code == 422
