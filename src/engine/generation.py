from langchain_google_genai import ChatGoogleGenerativeAI

class ChatModel():
    def __init__(self, model_name: str = "gemini-2.5-flash", google_api_key: str=""):
        self.chat_model = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key = google_api_key,
            temperature=1.0,
            max_tokens=None,
            timeout=None,
            max_retries=2
        )