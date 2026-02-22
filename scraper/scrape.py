import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import os

from typing import List, Dict

def get_response(url: str) -> str:
    html_response = requests.get(url).text
    return html_response

def download_image(image_url: str, save_path: str):
    try:
        response = requests.get(image_url) # Response Object
        with open(save_path, "wb") as f:
            f.write(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Failed to download image: {e}")


def parse_soup(url: str) -> BeautifulSoup:
    # Response by request return a Response Object. Content is in text attribute.
    html_response = requests.get(url).text
    soup = BeautifulSoup(html_response, 'html.parser')
    return soup

def get_cnn_articles(soup: BeautifulSoup, url: str) -> List[Dict[str, str]]:
    articles = []
    # Search by attrs: traditional like href, link, ... While new attrs like data-* is processed below
    main_container = soup.find_all(name = "div", attrs= {"data-component-name": "container"}) 
    for container in tqdm(main_container, desc = "Crawling articles"):
        headline_articles = container.find_all(name = "li")
        if headline_articles:
            for article in headline_articles:
                article_id = article.get("data-uri").split("/")[-1]
                article_link = url + article.get("data-open-link")
                article_category = article.get("data-section")
                articles.append({
                    "id": article_id,
                    "article_link": article_link,
                    "category": article_category
                })
    return articles

def extract_cnn_articles(article_soup: BeautifulSoup, article_id: str) -> Dict:
    articles = {}
    try: 
        article_title = article_soup.find("title").text
        main_content = article_soup.find(name = "main", class_ = "article__main")
        article_images = main_content.find_all(name = "div", attrs={"data-component-name": "image"})
        print(f"Article Images Section: {article_images}")
        print("1")
        # Download Image
        if not os.path.exists(f"data/{article_id}"):
            os.makedirs(f"data/{article_id}")
        for i, image in enumerate(article_images):
            image_url = image.get("data-url")
            print(f"Image URL: {image_url}")
            download_image(image_url, f"data/{article_id}/image_{i}.jpg")
        article_paragraphs = main_content.find_all(name = "p", attrs={"data-component-name": "paragraph"})
        print("2")
        article_content = ""
        for paragraph in article_paragraphs:
            article_content += paragraph.text
        articles["id"] =  article_id
        articles["title"] = article_title
        articles["content"] = article_content
        print("3")
        return articles
    except:
        print("Article not approriate !")
if __name__ == "__main__":
    # url =  "https://edition.cnn.com"
    # soup = parse_soup(url)
    # url = "https://edition.cnn.com/2026/02/22/europe/france-us-ambassador-quentin-deranque-death-intl"
    # html_response = get_response(url)
    # with open("data/article_1.html", 'w', encoding = 'utf-8') as f:
    #     f.write(html_response)
    # articles = get_cnn_articles(soup)
    with open("data/cnn.json", "r", encoding = "utf-8") as f:
        articles = json.load(f)
    
    article_0 = extract_cnn_articles(parse_soup(articles[0]["article_link"]), articles[0]["id"])
    id = article_0["id"]
    with open(f"data/{id}.json", "w", encoding = "utf-8") as f:
        json.dump(article_0, f, indent = 4)





