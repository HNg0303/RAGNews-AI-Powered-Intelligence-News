from fastapi import FastAPI
from fastapi.middleware import Middleware

from core.config import setting

app = FastAPI(title = setting.project_name)

@app.get("/hello")
async def start():
    print(f"Hello, Project set up successfully")