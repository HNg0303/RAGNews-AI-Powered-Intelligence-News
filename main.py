from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from src.engine.engine import RAGChain

from core.config import setting
from src.api.router import routers
from src.engine.indexing import indexing

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic ---
    # This runs ONCE when the server starts
    if not hasattr(app.state, "rag_chain"):
        print("🚀 Initializing RAG chain and loading models...")
        app.state.rag_chain = RAGChain(
            embedding_model=setting.embedding_model,
            reranking_model=setting.reranking_model,
            chat_model=setting.chat_model,
            cloud_uri=setting.zilliz_cloud_uri,
            cloud_api_key=setting.zilliz_cloud_api_key,
            google_api_key=setting.google_api_key
        )
        # indexing(app.state.rag_chain.retriever.vector_store)
        app.state.rag_chain.init_chain()
        print("✅ RAG chain initialized successfully.")
    
    yield  # The application runs here
    
    # --- Shutdown Logic ---
    # This runs when the server stops (e.g., to close DB connections)
    print("🛑 Shutting down: Closing connections...")

app = FastAPI(title = setting.project_name, lifespan = lifespan)

app.include_router(router = routers, prefix="/api")

app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["localhost:3000", "localhost:8501"],
        allow_methods=["*"],
        allow_headers=["*"]
)

