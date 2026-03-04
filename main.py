from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import setting
from src.api.router import routers

app = FastAPI(title = setting.project_name)

app.include_router(router = routers, prefix="/api")

app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["localhost:3000"],
        allow_methods=["*"],
        allow_headers=["*"]
)