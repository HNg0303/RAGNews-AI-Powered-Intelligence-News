import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
import json
import os

async def fetch_soup(session: aiohttp.ClientSession, url: str) -> BeautifulSoup:
    """
        Asynchronously fetch a url to beautiful soup.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        async with session.get(url = url, headers = headers) as response:
            response.raise_for_status()
            html = await response.text() # This where the function is asynchronous -> It has to wait for response
            return BeautifulSoup(html, "html.parser")
    except Exception as e:
        print(f"Error while fetching {url}: {e}")
        return None
    
async def download_image(session: aiohttp.ClientSession, url: str, save_path: str):
    """
        Asynchronously write image file to local path.
    """
    try:
        async with session.get(url = url) as response:
            if response.status == 200:
                async with aiofiles.open(save_path, "wb") as f:
                    await f.write(await response.read())
    except Exception as e:
        print(f"Error while saving image: {e}")

async def save_json(data: dict, save_path: str):
    """
        JSON Helper write asynchronously.
    """
    async with aiofiles.open(save_path, "w", encoding='utf-8') as f:
        await f.write(json.dumps(data, indent = 4, ensure_ascii=False))




