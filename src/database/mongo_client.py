from pymongo import MongoClient
from pathlib import Path
import json
from tqdm import tqdm

DATA_PATH = Path("data/raw_news")

# Define function to get DB.
def get_database(MONGO_URI: str, MONGO_DB_NAME: str):
    # Create a connection using MongoDB string
    client = MongoClient(MONGO_URI)

    # Connect to DATABASE NAME
    db = client[MONGO_DB_NAME]
    return db

def get_collection(collection_name: str, MONGO_URI: str, MONGO_DB_NAME: str):
    db = get_database(MONGO_URI=MONGO_URI, MONGO_DB_NAME=MONGO_DB_NAME)
    return db[collection_name]

def insert_data(db):
    for json_file in tqdm(DATA_PATH.iterdir(), desc = "Inserting document to MongoDB"):
        if json_file.is_file():
            with open(json_file, "r", encoding = "utf-8") as f:
                article = json.load(f)
            if article:
                db.insert_one(article)

if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    load_dotenv()
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

    db = get_collection(collection_name="Articles", MONGO_URI=MONGO_URI, MONGO_DB_NAME=MONGO_DB_NAME)
    insert_data(db)
        