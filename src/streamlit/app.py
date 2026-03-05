import streamlit as st
import json
import os
import random
from pathlib import Path
import datetime

from components.home import render_home
from components.article import render_article
from components.chat import render_chat

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
elif page == "chat":
    render_chat()