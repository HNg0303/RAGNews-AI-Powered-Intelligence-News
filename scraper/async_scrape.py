from scraper.async_utils import fetch_soup, save_json
from scraper.scrape import get_cnn_articles, get_apnews_articles, get_fp_articles, extract_cnn_articles, extract_apnews_articles, extract_fp_articles
import asyncio
import aiofiles
import aiohttp
import os
from typing import List, Dict
import tqdm.asyncio as tqdm_async
from tqdm import tqdm


########################
# 1. Get all links from base homepage.
########################

async def get_all_links(session: aiohttp.ClientSession, sources: Dict[str, str]) -> Dict[str, List[str]]:
    """
    From homepage of each source: 
    - Fetch soup html.
    - Get all links
    - Save links to json
    """
    print(f"Fetching all links from sources ...")
    try:
        soup = await asyncio.gather(
            fetch_soup(session, sources["cnn"]), 
            fetch_soup(session, sources["apnews"]), 
            fetch_soup(session, sources["fp"]), 
        )

        cnn_links = await get_cnn_articles(soup[0], sources["cnn"])
        ap_links = await get_apnews_articles(soup[1], sources["apnews"])
        fp_links = await get_fp_articles(soup[2], sources["fp"])

        await asyncio.gather(
            save_json(cnn_links, "data/general/cnn.json"),
            save_json(ap_links, "data/general/apnews.json"),
            save_json(fp_links, "data/general/fp.json"),
        )
        return {
            "cnn": cnn_links,
            "apnews": ap_links,
            "fp": fp_links
        }
    except Exception as e:
        print(f"Error fetching links: {e}")
        return None
    
###############
# 2. Content extraction
###############
async def get_all_content(session: aiohttp.ClientSession, all_links: Dict[str, List[str]]) -> Dict[str, str]:
    print(f"Extracting data ....")
    os.makedirs("data/raw_news", exist_ok=True)
    
    # Semaphore to prevent overwhelming servers (e.g., max 20 concurrent requests overall)
    sem = asyncio.Semaphore(20) 
    
    tasks = []
    
    # Queue up CNN tasks
    for article in tqdm(all_links["cnn"], desc="Gathering CNN Extraction tasks"):
        if not os.path.exists(f"data/raw_news/{article['id']}.json"):
            tasks.append(extract_cnn_articles(session, article, sem)) #Gathering couroutines not executing it with await.
            
    # # Queue up APNews tasks
    # for article in all_links["apnews"]:
    #     if not os.path.exists(f"data/raw_news/{article['id']}.json"):
    #         tasks.append(await extract_apnews_articles(session, article, sem))
            
    # Queue up FP tasks
    for article in tqdm(all_links["fp"], desc = "Gathering all Financial Post"):
        if not os.path.exists(f"data/raw_news/{article['id']}.json"):
            tasks.append(extract_fp_articles(session, article, sem))

    print(f"Starting extraction for {len(tasks)} new articles...")
    
    # Process them concurrently with a progress bar
    results = [await t for t in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Extracting")]
    
    # Save the successful results to disk
    save_tasks = []
    for result in results:
        if result and "id" in result:
            filepath = f"data/raw_news/{result['id']}.json"
            save_tasks.append(save_json(result, filepath))
            
    if save_tasks:
        await asyncio.gather(*save_tasks)
    print("Saved all new articles!")
    return results

async def main():
    sources = {
        "cnn": "https://edition.cnn.com",
        "apnews": "https://apnews.com",
        "fp": "https://financialpost.com"
    }
    # Share a single connection pool session across the entire script
    async with aiohttp.ClientSession() as session:
        all_links = await get_all_links(session, sources)
        if all_links is None:
            print(f"Cannot scrape links !")
            return
        await get_all_content(session, all_links)

if __name__ == "__main__":
    for dir_path in ["data/general", "data/finance", "data/images", "data/raw_news"]:
        os.makedirs(dir_path, exist_ok=True)
    asyncio.run(main())