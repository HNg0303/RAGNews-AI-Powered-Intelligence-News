import requests

def get_articles(url : str = "http://localhost:8000/api/article/get_articles"):
    """
        Call API from FastAPI server
    """
    try: 
        response = requests.get(url)
        if response.status_code==200:
            data = response.json()
            return data
        else:
            print(f"Status code: {response.status_code}. Message: {response}")

    except Exception as e:
        print(f"Error: {e}")

def get_image(url : str = "http://localhost:8000/api/image", article_id: str = ""):
    try:
        response = requests.get(f"{url}/{article_id}")
        if response.status_code==200:
            data = response.json()
            return data
        else:
            print(f"Status code: {response.status_code}. Message: {response}")

    except Exception as e:
        print(f"Error: {e}")

def get_article_by_id(url : str = "http://localhost:8000/api/article/get_article", article_id: str = ""):
    try:
        response = requests.get(f"{url}/{article_id}")
        if response.status_code==200:
            data = response.json()
            return data
        else:
            print(f"Status code: {response.status_code}. Message: {response}")
    
    except Exception as e:
        print(f"Error: {e}")