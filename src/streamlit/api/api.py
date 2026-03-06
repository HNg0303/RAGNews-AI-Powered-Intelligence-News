import requests

BACKEND_URL="https://ragnews-ai-powered-intelligence-news.onrender.com"

def get_articles(url : str = f"{BACKEND_URL}/api/article/get_articles"):
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

def get_image(article_id: str, url : str = f"{BACKEND_URL}/api/image"):
    try:
        response = requests.get(f"{url}/{article_id}")
        if response.status_code==200:
            data = response.json()
            return data
        else:
            print(f"Status code: {response.status_code}. Message: {response}")

    except Exception as e:
        print(f"Error: {e}")

def get_article_by_id(article_id: str, url : str = f"{BACKEND_URL}/api/article/get_article"):
    try:
        response = requests.get(f"{url}/{article_id}")
        if response.status_code==200:
            data = response.json()
            return data
        else:
            print(f"Status code: {response.status_code}. Message: {response}")
    
    except Exception as e:
        print(f"Error: {e}")

def get_rag_response(query: str, url = f"{BACKEND_URL}/api/agent/invoke"):
    payload = {
        "prompt": query 
    }
    try:
        response = requests.post(url, json = payload)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Status code: {response.status_code}. Message: {response}")
    except Exception as e:
        print(f"Error: {e}")
