from pymongo import MongoClient
from pathlib import Path
import json
from tqdm import tqdm

import base64

DATA_PATH = Path("data/raw_news")
IMAGE_PATH = Path("data/images")

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
                article_id = article["id"]
                article = db.find({"id": article_id})
                if not article: 
                    db.insert_one(article)

def add_image_data(db):
    for image_dir in tqdm(IMAGE_PATH.iterdir(), desc = "Adding Image data"):
        article_id = image_dir.stem
        images = []
        for image_file in image_dir.iterdir():
            if image_file.is_file():
                with open(image_file, "rb") as f:
                     images.append(base64.b64encode(f.read()).decode("utf-8"))
        query_filter = {
            "id": article_id
        }
        update = {
            "$set": 
            {
                "images": [f"data:image/jpg;base64,{encoded_string}" for encoded_string in images] if images else ""
            }
        }
        db.update_one(query_filter, update)

def delete_field(db, field: str):
    db.update_many(
        # Query
        {},
        # Filter
        {
            "$unset": {
                f"{field}": ""
            }
        }
    )

if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    load_dotenv()
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

    db = get_collection(collection_name="Articles", MONGO_URI=MONGO_URI, MONGO_DB_NAME=MONGO_DB_NAME)
    # insert_data(db)
    # add_image_data(db)
    delete_field(db, "images")
        