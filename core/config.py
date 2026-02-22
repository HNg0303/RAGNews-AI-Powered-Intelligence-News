from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict, List, Annotated

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file = ".env", env_file_encoding="utf-8") # Project Setting Configuration from dotenv file.

    project_name: str = "My Daily RAG Newspaper"
    host: str = "localhost:8000"

setting = Settings()

if __name__ == "__main__":
    print(f"Setting configuration: {setting.model_dump()}")