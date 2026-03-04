import streamlit as st
import json
import os
import random
from pathlib import Path
import datetime

from components.home import render_home
from components.article import render_article

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RAGNews - AI-Powered Intelligent News Source",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def apply_custom_css(css_file: str):
    """
        css_file: CSS Style file path.
    """
    with open(css_file) as f:
        css = f.read()
    st.markdown(f"<style>@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=DM+Sans:wght@300;400;500&display=swap');{css}</style>", unsafe_allow_html=True)

# ── RAG chatbot implementation ─────────────────────────────────────────────────

def _get_rag_chain():
    """Lazy initializer for the RAGChain stored in session_state."""
    if "rag_chain" not in st.session_state:
        from dotenv import load_dotenv
        from src.engine.engine import RAGChain

        load_dotenv()
        ZILLIZ_CLOUD_URI = os.getenv("ZILLIZ_CLOUD_URI")
        ZILLIZ_CLOUD_API_KEY = os.getenv("ZILLIZ_CLOUD_API_KEY")
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

        rag = RAGChain(
            embedding_model="BAAI/bge-base-en-v1.5",
            reranking_model="BAAI/bge-reranker-base",
            chat_model="gemini-2.5-flash",
            cloud_uri=ZILLIZ_CLOUD_URI,
            cloud_api_key=ZILLIZ_CLOUD_API_KEY,
            google_api_key=GOOGLE_API_KEY,
        )
        st.session_state.rag_chain = rag
    return st.session_state.rag_chain


def rag_agent_response(user_message: str, article: dict | None) -> str:
    """Invoke the RAG pipeline to answer a question.

    If an article is provided we optionally include its id/title in the
    query in order to encourage the retriever to filter by that context.
    """
    rag = _get_rag_chain()
    query = user_message
    if article:
        query = f"{user_message} [article_id:{article.get('id')}]"
    try:
        return rag.invoke(query)
    except Exception as exc:
        # fallback to a simple message on failure
        return f"Error contacting RAG backend: {exc}"


apply_custom_css("src/streamlit/styles.css")

# ── Session state ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"
if "current_article" not in st.session_state:
    st.session_state.current_article = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Router ────────────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "home":
    render_home()
elif page == "article":
    render_article()
# elif page == "chat":
#     render_chat()