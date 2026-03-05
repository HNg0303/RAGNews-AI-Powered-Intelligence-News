from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from src.engine.indexing import indexing 

agent_router = APIRouter(
    prefix="/agent",
    tags= ["agent"]
)

class QueryModel(BaseModel):
    prompt: str

class ResponseModel(BaseModel):
    response: str

@agent_router.post("/invoke")
async def invoke(
    request: Request,
    query: QueryModel,
):
    rag_chain = request.app.state.rag_chain
    try:
        answer = rag_chain.invoke(query.prompt)
        return ResponseModel(response = answer)
    except Exception as e:
        return HTTPException(status_code = 500, detail = str(e))

@agent_router.post("/index")
async def index(
    request: Request
):
    rag_chain = request.app.state.rag_chain
    indexing(rag_chain.retriever.vector_store)
    print(f"Indexing successfully")

