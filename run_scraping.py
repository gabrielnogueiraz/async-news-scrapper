import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.db import init_db, get_db
from src.scrapper import G1Scraper

async def main():
    print("Initializing database...")
    await init_db()
    
    print("Starting news scraping...")
    async for db in get_db():
        scraper = G1Scraper(db)
        news_added = await scraper.scrape()
        print(f"Successfully scraped and added {news_added} new articles")
        break

if __name__ == "__main__":
    asyncio.run(main())
