import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options 

def set_up(url: str):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    # Create Chrome options
    chrome_options = Options()
    # Add the user agent argument
    chrome_options.add_argument(f"--user-agent={user_agent}")
    chrome_options.add_argument(f"--headless=new")
    # Initialize the WebDriver with the custom options
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    return driver

def teardown(driver: webdriver):
    driver.quit()

def get_response(url: str) -> str:
    html_response = requests.get(url).text
    return html_response

def get_page_source(url: str, save_path: str = ""):
    try:
        driver = set_up(url)
        driver.implicitly_wait(2)
        html_source = driver.page_source
        if save_path != "":
            with open(save_path, "w", encoding = "utf-8") as f:
                f.write(html_source)
            print(f"Write HTML with Selenium WebDriver")
        teardown(driver)
        return html_source
    except Exception as e:
        print(f"Error: {e}. Callback to use requests")
        html_source = get_response(url)
        if save_path != "":
            with open(save_path, "w", encoding = "utf-8") as f:
                f.write(html_source)
            print(f"Write HTML with Request Library")
        return html_source

def download_image(image_url: str, save_path: str):
    try:
        response = requests.get(image_url) # Response Object
        with open(save_path, "wb") as f:
            f.write(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Failed to download image: {e}")

def parse_soup(url: str) -> BeautifulSoup:
    # Response by request return a Response Object. Content is in text attribute.
    try:
        html_response = get_page_source(url)
        soup = BeautifulSoup(html_response, 'html.parser')
        return soup
    except Exception as e:
        print(f"Error: {e}")