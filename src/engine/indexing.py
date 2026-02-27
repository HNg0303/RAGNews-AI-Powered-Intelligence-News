from src.database.vector_store import VectorStore
import os
from tqdm import tqdm
from pathlib import Path

import json

raw_news_source = Path("data/raw_news")

def indexing(vector_store: VectorStore):
    articles = []
    for source_path in tqdm(raw_news_source.iterdir(), desc = "Indexing sources"):
        source_name = str(source_path).split("/")[-1]
        for json_file in tqdm(source_path.iterdir(), desc = "Indexing article"):
            with open(json_file, "r", encoding="utf-8") as f:
                article = json.load(f)

            article["src"] = source_name
            articles.append(article)
    
    vector_store.add_documents(articles)
    print(f"Indexing successfully !")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    # Connect to CLOUD ZILLIZ built upon Milvus.
    ZILLIZ_CLOUD_URI = os.getenv("ZILLIZ_CLOUD_URI")
    ZILLIZ_CLOUD_API_KEY = os.getenv("ZILLIZ_CLOUD_API_KEY")

    vs = VectorStore(ZILLIZ_URI = ZILLIZ_CLOUD_URI, ZILLIZ_API_KEY=ZILLIZ_CLOUD_API_KEY)
    print(f"Successfully Connect to Zilliz Cloud VB\n\n")

    indexing(vs)
