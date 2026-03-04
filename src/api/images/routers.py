from fastapi import APIRouter
from src.schema.images import ImageResponse

from typing import List
import json

from pathlib import Path
import base64

IMAGE_PATH = Path("data/images/")

image_router = APIRouter(
    prefix = "/image",
    tags=["image"]
)

@image_router.get("/{article_id}")
async def get_article(article_id: str, response_model = List[ImageResponse]):
    # Current local storage
    image_path = IMAGE_PATH / article_id
    encoded_data = []
    for image in image_path.iterdir():
        if image.is_file():
            with open(image, "rb") as f:
                encoded_data.append(base64.b64encode(f.read()).decode("utf-8"))
    
    return [
        {
            "image_base64": f"data:image/jpeg;base64,{encoded_string}" for encoded_string in encoded_data
        }
    ]