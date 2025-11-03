from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import News


class TestNewsModel:
    @pytest.mark.asyncio
    async def test_create_news(self, db_session: AsyncSession):
        news = News(
            title="Teste de criação de notícia",
            url="https://g1.globo.com/test-create"
        )
        db_session.add(news)
        await db_session.commit()

        result = await db_session.execute(select(News))
        saved_news = result.scalar_one()

        assert saved_news.id is not None
        assert saved_news.title == "Teste de criação de notícia"
        assert saved_news.url == "https://g1.globo.com/test-create"
        assert isinstance(saved_news.created_at, datetime)

    @pytest.mark.asyncio
    async def test_news_unique_url(self, db_session: AsyncSession):
        news1 = News(
            title="Primeira notícia",
            url="https://g1.globo.com/unique-test"
        )
        db_session.add(news1)
        await db_session.commit()

        news2 = News(
            title="Segunda notícia com mesma URL",
            url="https://g1.globo.com/unique-test"
        )
        db_session.add(news2)

        with pytest.raises(Exception):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_news_repr(self, db_session: AsyncSession):
        news = News(
            title="Teste de representação muito longa que precisa ser truncada",
            url="https://g1.globo.com/test-repr"
        )
        db_session.add(news)
        await db_session.commit()

        repr_str = repr(news)
        assert "News" in repr_str
        assert "id=" in repr_str
        assert "title=" in repr_str

    @pytest.mark.asyncio
    async def test_news_created_at_auto(self, db_session: AsyncSession):
        news = News(
            title="Teste de timestamp automático",
            url="https://g1.globo.com/test-timestamp"
        )
        db_session.add(news)
        await db_session.commit()

        assert news.created_at is not None
        assert isinstance(news.created_at, datetime)
        assert news.created_at <= datetime.now(timezone.utc)

    @pytest.mark.asyncio
    async def test_query_news_by_id(self, db_session: AsyncSession):
        news = News(
            title="Teste de query por ID",
            url="https://g1.globo.com/test-query-id"
        )
        db_session.add(news)
        await db_session.commit()

        result = await db_session.execute(
            select(News).where(News.id == news.id)
        )
        found_news = result.scalar_one()

        assert found_news.id == news.id
        assert found_news.title == news.title

    @pytest.mark.asyncio
    async def test_query_news_by_url(self, db_session: AsyncSession):
        news = News(
            title="Teste de query por URL",
            url="https://g1.globo.com/test-query-url"
        )
        db_session.add(news)
        await db_session.commit()

        result = await db_session.execute(
            select(News).where(News.url == "https://g1.globo.com/test-query-url")
        )
        found_news = result.scalar_one()

        assert found_news.title == "Teste de query por URL"
