from utils import parse_soup, download_image
from bs4 import BeautifulSoup
import json
from typing import List, Dict
from tqdm import tqdm
import os

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

def extract_cnn_articles(article_soup: BeautifulSoup, article_id: str, article_link: str) -> Dict:
    articles = {}
    try: 
        article_title = article_soup.find("title").text
        main_content = article_soup.find(name = "main", class_ = "article__main")
        article_images = main_content.find_all(name = "div", attrs={"data-component-name": "image"})
        # Download Image
        if not os.path.exists(f"data/images/{article_id}"):
            os.makedirs(f"data/images/{article_id}")
        for i, image in enumerate(article_images):
            image_url = image.get("data-url")
            print(f"Image URL: {image_url}")
            download_image(image_url, f"data/images/{article_id}/image_{i}.jpg")
        article_paragraphs = main_content.find_all(name = "p", attrs={"data-component-name": "paragraph"})
        article_content = ""
        for paragraph in article_paragraphs:
            article_content += paragraph.text
        articles["id"] =  article_id
        articles["title"] = article_title
        articles["content"] = article_content
        articles["source"] = article_link
        return articles
    except:
        print("Article not approriate !")
        return None

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
    return articles

def extract_apnews_articles(soup: BeautifulSoup, article_id: str, article_link: str):
    article = {}
    try:
        content = ""
        page_content = soup.find(name = "div", class_ = "Page-content")
        title = page_content.find(name = "h1", class_ = "Page-headline").text
        main_content = page_content.find(name = "div", class_ = "Page-twoColumn")
        image_url = main_content.find(name = "img").get("src")
        if image_url:
            if not os.path.exists(f"data/images/{article_id}"):
                os.makedirs(f"data/images/{article_id}", exist_ok=False)
            download_image(image_url=image_url, save_path=f"data/images/{article_id}/image.jpg")
        paragraphs = main_content.find_all(name = "p")
        for p in paragraphs:
            content += p.text
        article["id"] = article_id
        article["title"] = title
        article["content"] = content
        article["source"] = article_link
        return article
    except Exception as e:
        print(f"Error: {e}")

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

def extract_fp_articles(article_soup: BeautifulSoup):
    articles = {}
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
        
        articles["id"] = id
        articles["title"] = title
        articles["subtitle"] = subtitle
        articles["content"] = content

        return articles
    except Exception as e:
        print(f"Error: {e}")

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

    

    
    


