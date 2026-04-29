import requests
from uuid import UUID

BACKEND_URL="http://localhost:8000"
MOCK_USER_ID = "b7a39ffc-6401-4dd3-87b1-2078ae2060b7"

def get_articles(limit: int = 20):
    """
        Call API from FastAPI server
    """
    try: 
        response = requests.get(f"{BACKEND_URL}/api/article/get_articles", params={"limit": limit})
        if response.status_code==200:
            data = response.json()
            return data
        else:
            print(f"Status code: {response.status_code}. Message: {response}")

    except Exception as e:
        print(f"Error: {e}")

def get_article_by_id(article_id: str):
    try:
        response = requests.get(f"{BACKEND_URL}/api/article/get_article/{article_id}")
        if response.status_code==200:
            data = response.json()
            return data
        else:
            print(f"Status code: {response.status_code}. Message: {response}")
    
    except Exception as e:
        print(f"Error: {e}")

def rag_chat(question: str, user_id: UUID, article_id: str = None):
    payload = {
        "question": question,
        "user_id": user_id,
        "article_id": article_id
    }
    try:
        response = requests.post(f"{BACKEND_URL}/api/rag/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Status code: {response.status_code}. Message: {response}")
    
    except Exception as e:
        print(f"Error: {e}")

def rag_insight(user_id: UUID, article_id: str):
    payload = {
        "user_id": user_id,
        "article_id": article_id
    }
    try:
        response = requests.post(f"{BACKEND_URL}/api/rag/insight", json=payload)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Status code: {response.status_code}. Message: {response}")
    
    except Exception as e:
        print(f"Error: {e}")
