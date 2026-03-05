from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.engine.engine import RAGChain

from core.config import setting
from src.api.router import routers

app = FastAPI(title = setting.project_name)

app.include_router(router = routers, prefix="/api")

app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["localhost:3000", "localhost:8501"],
        allow_methods=["*"],
        allow_headers=["*"]
)

rag_chain = RAGChain(
    embedding_model=setting.embedding_model,
    reranking_model=setting.reranking_model,
    chat_model=setting.chat_model,
    cloud_uri=setting.zilliz_cloud_uri,
    cloud_api_key=setting.zilliz_cloud_api_key,
    google_api_key=setting.google_api_key
)
rag_chain.init_chain()
app.state.rag_chain = rag_chain

print("Init RAG chain successfully")

