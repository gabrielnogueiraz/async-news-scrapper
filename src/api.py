from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db, init_db
from src.models import News
from src.schemas import ErrorResponse, NewsResponse, ScrapeResponse
from src.scrapper import G1Scraper


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Async News Scraper",
    description="High-performance asynchronous news scraping system",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "Async News Scraper",
        "status": "running",
        "endpoints": ["/news", "/scrape"],
    }


@app.get(
    "/news",
    response_model=List[NewsResponse],
    tags=["News"],
    summary="Get all news",
    description="Retrieve all stored news articles ordered by creation date (newest first)",
)
async def get_news(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await db.execute(
            select(News)
            .order_by(News.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        news = result.scalars().all()
        return [NewsResponse.model_validate(item) for item in news]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve news: {str(e)}",
        )


@app.post(
    "/scrape",
    response_model=ScrapeResponse,
    tags=["Scraping"],
    summary="Execute news scraping",
    description="Trigger a new scraping operation to collect latest news from G1",
    status_code=status.HTTP_200_OK,
)
async def scrape_news(db: AsyncSession = Depends(get_db)):
    try:
        scraper = G1Scraper(db)
        news_added = await scraper.scrape()

        return ScrapeResponse(
            success=True,
            news_added=news_added,
            message=f"Successfully scraped and added {news_added} new articles",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scraping failed: {str(e)}",
        )


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "async-news-scraper"}
