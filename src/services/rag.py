from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage, AIMessage
from langchain.agents import create_agent
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
from src.database.relational.session import AsyncSessionLocal, engine

from src.engine.retriever import Retriever
from core.config import setting
import asyncio

from src.database.crud.article import (
    save_summary,
    get_article
)
from src.database.crud.thread import (
    get_or_create_thread,
    append_message,
    get_thread_history,
    to_langchain_messages,
    get_global_thread,
    create_thread
)
from src.database.schema.thread import (
    MessageCreate,
    MessageMeta,
    RoleEnum, 
    CitationSchema,
    ThreadCreate
)

from typing import List, Dict

retriever = Retriever(
    embedding_model=setting.embedding_model,
    reranking_model=setting.reranking_model,
    URI=setting.zilliz_cloud_uri,
    API_KEY=setting.zilliz_cloud_api_key
)

chat_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key = setting.google_api_key,
    temperature=1.0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

def _format_langchain_documents(documents: List[Document])->List[Dict[str, str]]:
    docs = []
    for doc in documents:
        docs.append(
            {
                "article_id": doc.metadata['id'],
                "article_title": doc.metadata['title'],
                "article_content": doc.page_content
            }
        )
    return docs

@tool
def retrieve_all_docs(query: str) -> List[Document]: 
    """
        Retrieve documents that are highly related to the query
        query: The sentence query from user.
    """
    results = retriever.retrieve(query)
    results = _format_langchain_documents(results)
    return results


# Database Aware tools
def make_retrieve_tool(db: AsyncSession):
    """
    Factory that injects the DB session into the retrieve tool.
    Called once per request — avoids global DB state.
    """
    @tool
    async def retrieve_by_id(article_id: str) -> str:
        """
            Return article by ID
        """
        article = await get_article(db, article_id)
        if not article:
            return f"Article {article_id} not found."
        return article

    return retrieve_by_id

def make_summarize_tool(db: AsyncSession):
    """
    Factory that injects the DB session into the summarize tool.
    Called once per request — avoids global DB state.
    """
    @tool
    async def summarize_article(article_id: str) -> str:
        """
        Return a structured summary of an article.
        Checks DB first — only calls Gemini if the article is not yet summarized.
        Always call this when a user opens an article page.
 
        Args:
            article_id: ID of the article to summarize.
        """
        article = await get_article(db, article_id)
        if not article:
            return f"Article {article_id} not found."
 
        # Cache hit — return stored summary instantly
        if article.is_summarized and article.summary:
            return article.summary
 
        # Cache miss — generate with Gemini
        messages = [
            SystemMessage(content=(
                "You are a news summarizer. Given an article, return:\n"
                "1. A one-paragraph main summary (3-4 sentences)\n"
                "2. Three bullet points of the most important facts\n\n"
                "Format:\nSUMMARY:\n<paragraph>\n\nKEY POINTS:\n• ...\n• ...\n• ..."
            )),
            HumanMessage(content=article.content or "No content available."),
        ]
        response = await chat_model.ainvoke(messages)
        summary = response.content
 
        # Persist to DB — next call is a cache hit
        await save_summary(db, article_id, summary)
 
        return summary
 
    return summarize_article


# ══════════════════════════════════════════════════════════════════════════════
# RAG AGENT SERVICE
# ══════════════════════════════════════════════════════════════════════════════
 
SYSTEM_PROMPT = """You are RAGNews Assistant, an intelligent news agent.
 
Your capabilities:
- Answer questions about current news using retrieved articles.
- Summarize specific articles on demand.
- Answer questions scoped to a single article the user is reading.
 
Rules:
1. ALWAYS use retrieve_all_docs for general questions (homepage mode).
2. ALWAYS use retrieve_docs_by_article when article_id context is provided (article mode).  
3. ALWAYS call summarize_article when a user opens a new article page.
4. Base your answers ONLY on retrieved content — never hallucinate facts.
5. When citing sources, include the article title and source name.
6. If no relevant documents are found, say so clearly.
 
Response format for QnA:
- Answer the question directly and concisely
- End with: "Sources: [Title — Source]" for each article used
"""
 
 
class RAGService:
    """
    Production RAG service exposing two public methods:
      - chat()     → stateful conversation (loads + saves history to PostgreSQL)
      - summarize() → one-shot article summarization (no thread needed)
 
    Usage in FastAPI:
        rag = RAGService()
 
        @router.post("/chat")
        async def chat(req: QnARequest, db: AsyncSession = Depends(get_db)):
            return await rag.chat(db, req.user_id, req.question, req.article_id, req.thread_id)
    """
 
    def __init__(self):
        self._llm = chat_model
        self._static_tools = [retrieve_all_docs]
 
    def _build_agent(self, db: AsyncSession):
        """
        Build a fresh agent per request — injects DB-aware summarize tool.
        LangGraph ReAct agent handles tool calling loop automatically.
        """
        tools = self._static_tools + [make_summarize_tool(db), make_retrieve_tool(db)]
        agent = create_agent(
            model=self._llm,
            tools=tools,
            system_prompt=SYSTEM_PROMPT,          # system prompt injected here
        )
        print(f"Agent created with {tools}")
        return agent
    
    async def gather_insights(
            self,
            db: AsyncSession,
            user_id: UUID,
            article_id: str
    ) -> dict:
        """
        Entry point when going into an Article:
        - Check if the article is summarized.
        - If not, call summaize_article() to summarize article and save summary.
        - Call retrieve_all_docs() to get relevant documents to the summary of the document.
        - Return structured dictionary: 
        """
        if article_id is None:
            return {}
        article = await get_article(db, article_id)
        is_summarized = article.is_summarized
        if is_summarized:
            article_summary = article.summary
        article_content = article.content
        # ── 2. Summarize if needed ────────────────────────────────────────────
        if article.is_summarized:
            article_summary = article.summary
        else:
            summarize_tool = make_summarize_tool(db)
            article_summary = await summarize_tool.ainvoke({"article_id": str(article_id)})
        
        await save_summary(db, article_id, article_summary)

        # ── 3. Build prompt for insight agent ─────────────────────────────────
        prompt = (
            f"You are analyzing a news article to surface key insights and related context.\n\n"
            f"Article ID: {article_id}\n"
            f"Article Summary:\n{article_summary}\n\n"
            f"Your tasks:\n"
            f"1. Identify the 3-5 most important themes or takeaways from this article.\n"
            f"2. Use retrieve_all_docs to find related articles from the knowledge base.\n"
            f"3. For each related article found, briefly explain its relevance to this article.\n"
            f"4. Return your analysis in a structured format."
        )

        # ── 4. Run agent ──────────────────────────────────────────────────────
        agent = self._build_agent(db)
        agent_input = {"messages": [HumanMessage(content=prompt)]}
        result = await agent.ainvoke(agent_input)

        # ── 5. Extract AI response ────────────────────────────────────────────
        ai_message: AIMessage = result["messages"][-1]

        if isinstance(ai_message.content, list):
            insights_text = " ".join(
                block["text"]
                for block in ai_message.content
                if isinstance(block, dict) and block.get("type") == "text"
            )
        else:
            insights_text = str(ai_message.content)

        # ── 6. Extract citations from retrieval tool calls ────────────────────
        citations = self._extract_citations(result["messages"])

        # ── 7. Return structured response ─────────────────────────────────────
        return {
            "article_id":   str(article_id),
            "summary":      article_summary,
            "insights":     insights_text,
            "related":      [c.model_dump() for c in citations],
        }

    async def chat(
        self,
        db: AsyncSession,
        user_id: UUID,
        question: str,
        article_id: str = None,
    ) -> dict:
        """
        Main chat entrypoint. Handles full lifecycle:
          1. Get or create thread
          2. Load conversation history from PostgreSQL
          3. Prepend article_id context to query if in article mode
          4. Run LangGraph agent
          5. Extract citations from tool outputs
          6. Persist human + AI messages to DB
          7. Return structured response
 
        Args:
            db:         Async SQLAlchemy session (injected by FastAPI)
            user_id:    UUID of the current user
            question:   The user's question
            article_id: If set, scopes retrieval to this article (article mode)
            thread_id:  Existing thread UUID — creates new thread if None
        """
        # A thread is found and defined by (user, article) pair for article thread else a global thread.
        # ── 1. Thread management ──────────────────────────────────────────────
        if article_id:
            thread = await get_or_create_thread(db, user_id, article_id)
        else:
            thread = await get_global_thread(db, user_id)
            if thread is None:
                # Create first global thread
                thread = await create_thread(db, ThreadCreate(user_id = user_id))
 
        # ── 2. Load conversation history ──────────────────────────────────────
        # Sliding window: last 20 messages to stay within context limits
        history: list[BaseMessage] = await self._load_history(db, thread.thread_id, 5)
 
        # ── 3. Build agent input ──────────────────────────────────────────────
        # Inject article_id into the query so the agent picks the right tool
        if article_id:
            agent_question = (
                f"[ARTICLE MODE - article_id: {article_id}]\n"
                f"User question: {question}"
            )
        else:
            agent_question = question
 
        agent_input = {
            "messages": history + [HumanMessage(content=agent_question)]
        }
 
        # ── 4. Run agent ──────────────────────────────────────────────────────
        agent = self._build_agent(db) # DB-aware agent to prevent global database state.
        result = await agent.ainvoke(agent_input)
 
        # ── 5. Extract AI response and citations ──────────────────────────────
        ai_message: AIMessage = result["messages"][-1]

        # ROBUST text extraction if the content of LLM contains: [{"type": "", "text": }, {"type": "reasoning", "Text"}
        if isinstance(ai_message.content, list):
            answer = " ".join(
                block["text"] 
                for block in ai_message.content 
                if isinstance(block, dict) and block.get("type") == "text"
            )
        else:
            answer = str(ai_message.content)

        # Relational Newspaper.
        citations = self._extract_citations(result["messages"])
 
        meta = MessageMeta(
            citations=citations,
            tool_calls=[
                {"name": msg.name, "output": msg.content}
                for msg in result["messages"]
                if hasattr(msg, "name") and msg.name  # ToolMessage nodes
            ],
        )
 
        # ── 6. Persist to PostgreSQL ──────────────────────────────────────────
        human_msg = await append_message(
            db, thread.thread_id,
            MessageCreate(role=RoleEnum.human, content=question),
        )
        ai_msg_row = await append_message(
            db, thread.thread_id,
            MessageCreate(role=RoleEnum.ai, content=answer, meta=meta),
        )
 
        # ── 7. Return structured response ─────────────────────────────────────
        return {
            "thread_id":  str(thread.thread_id),
            "message_id": str(ai_msg_row.message_id),
            "answer":     answer,
            "citations":  [c.model_dump(mode='json') for c in citations],
        }
    
    async def _load_history(
        self, db: AsyncSession, thread_id: UUID, limit: int = 20
    ) -> list[BaseMessage]:
        """
        Load thread history from PostgreSQL and convert to LangChain messages.
        Sliding window of last `limit` messages to cap context size.
        """
        db_messages = await get_thread_history(db, thread_id, limit=limit)
        lc_dicts = await to_langchain_messages(db_messages)
 
        # Convert dicts to LangChain BaseMessage objects
        result = []
        for msg in lc_dicts:
            if msg["role"] == "human":
                result.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "ai":
                result.append(AIMessage(content=msg["content"]))
        return result
 
    def _extract_citations(self, messages: list) -> list[CitationSchema]:
        """
        Parse tool output messages to extract article citations.
        Tool outputs are list[dict] from retrieve_all_docs / retrieve_docs_by_article.
        """
        citations = []
        seen_ids = set()
 
        for msg in messages:
            # ToolMessage nodes have a .content that is the tool's return value
            if not hasattr(msg, "name") or not msg.name:
                continue
            if msg.name not in ("retrieve_all_docs", "retrieve_by_id", "summarize_article"):
                continue
 
            # msg.content is a JSON string of list[dict] when returned from tool
            import json
            try:
                docs = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
            except (json.JSONDecodeError, TypeError):
                continue
 
            if not isinstance(docs, list):
                continue
 
            for doc in docs:
                article_id = doc.get("article_id")
                if not article_id or article_id in seen_ids:
                    continue
                seen_ids.add(article_id)
                citations.append(CitationSchema(
                    article_id=article_id,
                    title=doc.get("article_title", "Unknown"),
                ))
 
        return citations
    
rag_service = RAGService()
user_id = "b7a39ffc-6401-4dd3-87b1-2078ae2060b7"
article_id = "c9f6937d-b967-4070-bed1-98d9c1ab3ef8"

async def main():
    async with AsyncSessionLocal() as session: # Local Database Session of Database Engine to Database URL
        results = await rag_service.gather_insights(session, user_id, article_id)
        await session.commit()  # Commit() changes of the local session
        print(results)
        return results

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    result = asyncio.run(main())
    print(result)

