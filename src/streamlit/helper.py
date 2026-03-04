import streamlit as st

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

def nav(page: str, article=None):
    st.session_state.page = page
    if article is not None:
        st.session_state.current_article = article
    if page == "chat" and article is not None:
        st.session_state.chat_history = []   # fresh chat per article