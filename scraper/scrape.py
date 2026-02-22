import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json

def parse_soup(url: str) -> BeautifulSoup:
    # Response by request return a Response Object. Content is in text attribute.
    html_response = requests.get(url).text
    soup = BeautifulSoup(html_response, 'html.parser')
    return soup

if __name__ == "__main__":
    url =  "https://edition.cnn.com"
    soup = parse_soup(url)
    articles = []

    # Search by attrs: traditional like href, link, ... While new attrs like data-* is processed below
    main_container = soup.find_all(name = "div", attrs= {"data-component-name": "container"}) 
    for container in tqdm(main_container, desc = "Crawling articles"):
        headline_articles = container.find_all(name = "li")
        if headline_articles:
            for article in headline_articles:
                article_link = url + article.get("data-open-link")
                article_category = article.get("data-section")
                articles.append({
                    "article_link": article_link,
                    "category": article_category
                })
    
    print(f"Sample: {articles[0]}")
    
    with open("data/cnn.json", "w", encoding = "utf-8") as f:
        json.dump(articles, f, indent = 4)





