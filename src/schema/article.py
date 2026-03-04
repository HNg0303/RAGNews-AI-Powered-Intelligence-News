from pydantic import BaseModel, Base64Str

class Article(BaseModel):
    id: str
    title: str
    content: str
    source: str
