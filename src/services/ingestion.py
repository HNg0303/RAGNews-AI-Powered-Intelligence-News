"""
Ingestion Service: Automatic News Crawling and Indexing into Vector Database and Relational Database.
"""
import aiohttp
import asyncio
from typing import Dict, List
from tqdm import tqdm
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import setting
from scraper.async_scrape import get_all_content, get_all_links
from src.database.relational.session import AsyncSessionLocal
from src.database.vector_store import VectorStore
from src.database.cloudinary_client import get_client, upload_to_cloudinary
from src.database.crud.article import create_article, get_article
from src.database.schema.article import ArticleCreate

class IngestionService():
    def __init__(self, zilliz_cloud: str, zilliz_api_key: str, cloudinary_name: str, cloudinary_api_key: str, cloudinary_api_secret: str):
        self.semaphore = asyncio.Semaphore(20)
        self.sources = {
            "cnn": "https://edition.cnn.com",
            "apnews": "https://apnews.com",
            "fp": "https://financialpost.com"
        }
        self.all_links: Dict[str, List[str]] = {}
        self.all_articles: List[Dict[str, str]] = []
        self.vector_store = VectorStore(
            ZILLIZ_API_KEY=zilliz_api_key,
            ZILLIZ_URI=zilliz_cloud,
        )
        self.cloudinary = get_client(
            cloudinary_api_key=cloudinary_api_key,
            cloudinary_api_secret=cloudinary_api_secret,
            cloudinary_cloud_name=cloudinary_name
        )
    
    async def crawl(self):
        async with aiohttp.ClientSession() as session: 
            self.all_links = await get_all_links(session=session, sources = self.sources)
            self.all_articles = await get_all_content(session=session, all_links=self.all_links)

    async def index(self):
        await self.crawl()
        print("Indexing and Populating Database....")
        # Can include NoneType article -> Access page_content in vector_store -> Error
        try:
            articles = [article for article in self.all_articles if article is not None]
            # self.vector_store.add_documents(articles) # Index document into the Milvus Vector Database
            async with AsyncSessionLocal() as db:
                for article in tqdm(articles, desc = "Uploading images and Database"):
                    local_image_url = article["local_image_url"]
                    image_url = upload_to_cloudinary(self.cloudinary, f"./{local_image_url}", article["id"])
                    article_create = ArticleCreate(
                        title=article['title'],
                        subtitle = article['subtitle'],
                        content = article["content"],
                        image_url = image_url,
                        article_id = article['id'],
                        created_at = datetime.now(timezone.utc)
                    )
                    art = await get_article(db, article['id'])
                    if art is None:
                        _ = await create_article(db, article_create) # Database Transaction is different from scraping. We cannot gather tasks and run concurrently. We have to asssure consistency.
                await db.commit()
                print(f"Done indexing articles")
        except Exception as e:
            print(f"Errors while indexing : {e}")


ingestion_service = IngestionService(
    zilliz_api_key=setting.zilliz_cloud_api_key,
    zilliz_cloud=setting.zilliz_cloud_uri,
    cloudinary_name=setting.cloudinary_cloud_name,
    cloudinary_api_secret=setting.cloudinary_api_secret,
    cloudinary_api_key=setting.cloudinary_api_key
)

if __name__ == "__main__":
    asyncio.run(ingestion_service.index())

