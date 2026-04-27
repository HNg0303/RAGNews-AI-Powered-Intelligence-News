from async_utils import fetch_soup, download_image
from bs4 import BeautifulSoup
import json
from typing import List, Dict
from tqdm import tqdm
import os
import asyncio
import aiohttp
import aiofiles

#### 1. Get articles link #####

def get_cnn_articles(soup: BeautifulSoup, url: str) -> List[Dict[str, str]]:
    articles = []
    # Search by attrs: traditional like href, link, ... While new attrs like data-* is processed below
    main_container = soup.find_all(name = "div", attrs= {"data-component-name": "container"}) 
    for container in tqdm(main_container, desc = "Crawling CNN articles"):
        if container:
            headline_articles = container.find_all(name = "li")
            if headline_articles:
                for article in headline_articles:
                    try:
                        article_id = article.get("data-uri").split("/")[-1]
                        article_link = url + article.get("data-open-link")
                        article_category = article.get("data-section")
                        articles.append({
                            "id": article_id,
                            "article_link": article_link,
                            "category": article_category
                        })
                    except:
                        print("No attributes")
    return articles

def get_apnews_articles(soup: BeautifulSoup, url: str) -> List[Dict[str, str]]:
    articles = []
    subheader_top_stories = soup.find_all(name = "div", class_ = "Subheader-Top-Stories")
    for top_stories in tqdm(subheader_top_stories, desc = "Crawling APNews Stories"):
        stories = top_stories.find_all(name = 'a')
        for story in stories:
            article_link = story.get("href")
            articles.append({
                "id": article_link.split('-')[-1],
                "article_link": article_link,
                "title": story.text
            })
    return 

def get_fp_articles(soup: BeautifulSoup, url: str) -> List[Dict[str, str]]:
    articles = []
    try:
        article_card = soup.find_all(name = "div", class_ = "article-card__details")
        for card in tqdm(article_card, desc = "Crawling FinancialPost articles"):
            article_related = card.find(name = "a", class_ = "article-card__link")
            if article_related:
                article_link = article_related.get("href")
                article_title = article_related.get("aria-label")
                articles.append({
                    "id": card.parent.get("data-article-id"),
                    "article_link": url + article_link,
                    "title": article_title  
                })
        return articles
    except Exception as e:
        print(f"Error: {e}")

"""
#### 2. Content Extractor #####
"""

async def extract_cnn_articles(session: aiohttp.ClientSession, article: dict, sem: asyncio.Semaphore) -> Dict[str, str]:
    async with sem: ## Semaphore for limit concurrency
        article_soup = await fetch_soup(session, article["article_link"])
        if not article_soup:
            return None
        try: 
            article_title = article_soup.find("title").text
            main_content = article_soup.find(name = "main", class_ = "article__main")
            article_images = main_content.find_all(name = "div", attrs={"data-component-name": "image"})
            # Download Image
            img_dir = f"data/images/{article["id"]}"
            if not os.path.exists(img_dir):
                os.makedirs(img_dir, exist_ok = True)
            image_tasks = []
            for i, image in enumerate(article_images):
                image_url = image.get("data-url")
                if image_url:
                    await image_tasks.append(download_image(session, image_url, f"{img_dir}/image_{i}.jpg")) # Async function
            await asyncio.gather(*image_tasks) # Await for download all images at once
            article_paragraphs = main_content.find_all(name = "p", attrs={"data-component-name": "paragraph"})
            article_content = ""
            for paragraph in article_paragraphs:
                article_content += paragraph.text
            return {
                "id" :  article["id"],
                "title": article_title,
                "content": article_content,
                "source": article["article_link"]
            }
        except Exception as e:
            print(f"Encounter error while extracting CNN Article: {e}")
            return None

async def extract_apnews_articles(session: aiohttp.ClientSession, article: dict, sem: asyncio.Semaphore) -> Dict[str, str]:
    async with sem: ## Semaphore for limit concurrency
        soup = await fetch_soup(session, article["article_link"])
        if not soup:
            return None
        try:
            content = ""
            page_content = soup.find(name = "div", class_ = "Page-content")
            title = page_content.find(name = "h1", class_ = "Page-headline").text
            main_content = page_content.find(name = "div", class_ = "Page-twoColumn")
            image_url = main_content.find(name = "img").get("src")
            img_dir = f"data/images/{article["id"]}"
            if not os.path.exists(img_dir):
                os.makedirs(img_dir, exist_ok = True)
            if image_url:
                await download_image(session, image_url, f"{img_dir}/image.jpg")# Async function
            paragraphs = main_content.find_all(name = "p")
            for p in paragraphs:
                content += p.text
            return {
                "id" :  article["id"],
                "title": title,
                "content": content,
                "source": article["article_link"]
            }
        except Exception as e:
            print(f"Encounter error while extracting APNews Article: {e}")
            return None

async def extract_fp_articles(session: aiohttp.ClientSession, article: dict, sem: asyncio.Semaphore) -> Dict[str, str]:
     async with sem: ## Semaphore for limit concurrency
        article_soup = await fetch_soup(session, article["article_link"])
        if not article_soup:
            return None
        try:
            main_content = article_soup.find(name = "main", id = "main-content")
            content = ""

            header_content =  main_content.find(name = "div", class_ = "story-v2")
            id = header_content.find(name = "article").get("data-wcm-id")
            title = header_content.find(name = "h1").text
            subtitle = header_content.find(name = "p").text

            article_content = main_content.find(name = "div", class_ = "story-v2-block-content")
            paragraphs = article_content.find_all("p")
            for p in paragraphs:
                content += p.text
            
            return {
                "id": id,
                "title": title,
                "subtitle": subtitle,
                "content": content,
                "source": article["article_link"]
            }
        except Exception as e:
            print(f"Encounter error while extracting Finanical Post Article: {e}")
            return None

def get_all_articles(urls: dict[str, str]):
    """
        Input is dict of 
            {
                "news source": "source_url"
            }
    """
    print(f"Getting articles for extracting!")
    for source_name, source_url in urls.items():
        if source_name == "cnn":
            article_links = get_cnn_articles(parse_soup(source_url), url = source_url)
            with open("data/general/cnn.json", "w", encoding = "utf-8") as f:
                json.dump(article_links, f, indent = 4)
        
        if source_name == "apnews":
            article_links = get_apnews_articles(parse_soup(source_url), url = source_url)
            with open("data/general/apnews.json", "w", encoding = "utf-8") as f:
                json.dump(article_links, f, indent = 4)
        
        if source_name == "fp":
            article_links = get_fp_articles(parse_soup(source_url), url = source_url)
            with open("data/finance/fp.json", "w", encoding = "utf-8") as f:
                json.dump(article_links, f, indent = 4)

def extract_all_articles(all_urls: dict[str, str]):
    # all_articles = []
    all_sources = {
        "cnn": "data/general/cnn.json",
        "apnews": "data/general/apnews.json",
        "fp": "data/finance/fp.json"
    }
    for name, source in all_sources.items():
        with open(f"{source}","r", encoding = "utf-8") as f:
            all_articles_link = json.load(f)
        if name == "apnews":
            print(f"Extracting articles from APNews.\n")
            for article in tqdm(all_articles_link, desc = "Extracting APNews Articles"):
                if not os.path.exists(f"data/raw_news/{article['id']}.json"):
                    article_result = extract_apnews_articles(parse_soup(article["article_link"]), article["id"], article["article_link"])
                    if article_result:
                        with open(f"data/raw_news/{article['id']}.json", "w", encoding = "utf-8") as f:
                            json.dump(article_result, f, indent = 4)
        
        elif name == "cnn":
            print(f"Extracting articles from CNN.\n")
            for article in tqdm(all_articles_link, desc = "Extracting CNN Articles"):
                if not os.path.exists(f"data/raw_news/{article['id']}.json"):
                    article_result = extract_cnn_articles(parse_soup(article["article_link"]), article["id"], article["article_link"])
                    if article_result:
                        with open(f"data/raw_news/{article['id']}.json", "w", encoding = "utf-8") as f:
                            json.dump(article_result, f, indent = 4)

        elif name == "fp":
            print(f"Extracting articles from Financial Post.\n")
            for article in tqdm(all_articles_link, desc = "Extracting Financial Post Articles"):
                if not os.path.exists(f"data/raw_news/{article['id']}.json"):
                    article_result = extract_fp_articles(parse_soup(article["article_link"]))
                    with open(f"data/raw_news/{article['id']}.json", "w", encoding = "utf-8") as f:
                        json.dump(article_result, f, indent = 4)
    print("Save all articles !")

if __name__ == "__main__":
    # Get new articles everyday
    all_sources = {
        "cnn": "https://edition.cnn.com",
        "apnews": "https://apnews.com",
        "fp": "https://financialpost.com"
    }
    get_all_articles(all_sources)
    extract_all_articles(all_sources)

    

    
    


