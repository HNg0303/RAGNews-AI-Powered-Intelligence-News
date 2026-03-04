import streamlit as st
import json
import os
import random
from pathlib import Path
import datetime

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

# ── Helpers ─────────────────────────────────────────────────────────────────────

def short_title(title: str, words: int = 12) -> str:
    parts = title.split()
    return " ".join(parts[:words]) + ("…" if len(parts) > words else "")


def strip_source(title: str) -> str:
    """Remove ' | Source' suffix from titles."""
    if " | " in title:
        return title.rsplit(" | ", 1)[0]
    return title

def no_img_placeholder(height: int, emoji: str = "📄"):
    return (
        f'<div style="height:{height}px;background:linear-gradient(135deg,#1a1a1a,#3d3d3d);'
        f'display:flex;align-items:center;justify-content:center;font-size:2.5rem;">{emoji}</div>'
    )


# ── Session state ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"
if "current_article" not in st.session_state:
    st.session_state.current_article = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def nav(page: str, article=None):
    st.session_state.page = page
    if article is not None:
        st.session_state.current_article = article
    if page == "chat" and article is not None:
        st.session_state.chat_history = []   # fresh chat per article

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

# ── PAGE: ARTICLE ─────────────────────────────────────────────────────────────
def render_article():
    art = st.session_state.current_article
    if not art:
        nav("home"); st.rerun(); return

    # Nav bar
    c1, c2, c3 = st.columns([2, 2, 8])
    with c1:
        st.markdown('<div class="btn-muted">', unsafe_allow_html=True)
        if st.button("← Headlines", key="back_home"):
            nav("home"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="btn-chat">', unsafe_allow_html=True)
        if st.button("💬 Ask AI", key="go_chat"):
            nav("chat", art); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    img_path = get_image_path(art["id"])
    title    = strip_source(art["title"])

    st.markdown(f"""
    <div class="article-header">
      <div class="article-kicker">News</div>
      <div class="article-title">{title}</div>
      <div class="article-meta">NewsFlow · AI Curated</div>
    </div>
    """, unsafe_allow_html=True)

    if img_path:
        col, _ = st.columns([2, 1])
        with col:
            st.image(str(img_path), use_container_width=True)

    content    = art.get("content", "").strip()
    paras      = [p.strip() for p in content.split("\n") if p.strip()]
    html_paras = "".join(f"<p>{p}</p>" for p in paras)
    st.markdown(f'<div class="article-content">{html_paras}</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)

# ── PAGE: CHATBOT ─────────────────────────────────────────────────────────────
def render_chat():
    art = st.session_state.current_article

    # Nav bar
    c1, c2, _ = st.columns([2, 2, 8])
    with c1:
        st.markdown('<div class="btn-muted">', unsafe_allow_html=True)
        if st.button("← Headlines", key="chat_home"):
            nav("home"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        if art:
            st.markdown('<div class="btn-muted">', unsafe_allow_html=True)
            if st.button("← Article", key="chat_article"):
                nav("article"); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="chat-page-header">
      <div class="chat-page-title">📰 Ask the Article</div>
      <div class="chat-page-sub">RAG-powered · Source-grounded answers</div>
    </div>
    """, unsafe_allow_html=True)

    # Article context pill
    if art:
        st.markdown(f"""
        <div class="chat-article-ctx">
          <strong>Discussing</strong>
          {strip_source(art['title'])}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="chat-article-ctx">
          <strong>General mode</strong>
          No article selected — ask anything about the news.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # ── Message history ──
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="chat-empty-state">
          <div class="chat-empty-icon">💬</div>
          Ask a question about this article and the AI will retrieve relevant context to answer it.
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            content = msg["content"]
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="cmsg-wrap-user">
                  <div class="cmsg-user">{content}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="cmsg-wrap-bot">
                  <div class="cmsg-bot">
                    <div class="cmsg-label">RAG Agent</div>
                    {content}
                  </div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # ── Input ──
    user_input = st.chat_input("Ask a question about this article…")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("Retrieving context…"):
            reply = rag_agent_response(user_input, art)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

    # Clear button (only if there's history)
    if st.session_state.chat_history:
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="btn-muted">', unsafe_allow_html=True)
        if st.button("Clear conversation", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ── Router ────────────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "home":
    render_home()
elif page == "article":
    render_article()
elif page == "chat":
    render_chat()