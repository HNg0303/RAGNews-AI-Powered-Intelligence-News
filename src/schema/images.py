from pydantic import BaseModel, Base64Str

class ImageResponse(BaseModel):
    image_base64: Base64Str