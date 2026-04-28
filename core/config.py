from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict, List, Annotated

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file = ".env", env_file_encoding="utf-8") # Project Setting Configuration from dotenv file.

    project_name: str = "My Daily RAG Newspaper"
    host: str = "localhost:8000"
    allow_origins: List[str]

    # External API Key
    google_api_key: str
    zilliz_cloud_uri: str
    zilliz_cloud_api_key: str

    # Models
    embedding_model: str
    reranking_model: str
    chat_model: str

    # PostgreSQL
    postgres_server: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str

    # Cloudinary
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str


setting = Settings()

if __name__ == "__main__":
    print(f"Setting configuration: {setting.model_dump()}")