"""
The News Dispatch — Streamlit RAG News App
==========================================
Run:  streamlit run app.py
"""

import streamlit as st
import requests

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="the news dispatch.",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded", # <-- Changed from "collapsed"
)

# ══════════════════════════════════════════════════════════════════════════════
#  API CALLS
# ══════════════════════════════════════════════════════════════════════════════

BACKEND_URL = "http://localhost:8000"
MOCK_USER_ID = "b7a39ffc-6401-4dd3-87b1-2078ae2060b7"

FALLBACK_IMAGES = [
    "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80",
    "https://images.unsplash.com/photo-1495020689067-958852a7765e?w=800&q=80",
    "https://images.unsplash.com/photo-1526280760714-f9e8b26f8533?w=800&q=80",
    "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800&q=80",
    "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800&q=80",
    "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
    "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
    "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
    "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
    "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
]


def _safe_image(art: dict, index: int = 0) -> str:
    """Get a safe image URL from article data, with fallback support."""
    if not isinstance(art, dict):
        return FALLBACK_IMAGES[index % len(FALLBACK_IMAGES)]
    
    # Try multiple image field names
    for key in ("image_url", "url_to_image", "thumbnail", "image", "img"):
        url = art.get(key, "")
        if url and isinstance(url, str) and str(url).startswith("http"):
            return url
    
    # Return fallback image
    return FALLBACK_IMAGES[index % len(FALLBACK_IMAGES)]


def api_get_articles(limit: int = 20):
    try:
        r = requests.get(
            f"{BACKEND_URL}/api/article/get_articles",
            params={"limit": limit},
            timeout=8,
        )
        if r.status_code == 200:
            return r.json()
        st.warning(f"API returned {r.status_code}")
    except Exception as e:
        st.warning(f"Cannot reach backend: {e}")
    return []


def api_get_article(article_id: str):
    try:
        r = requests.get(
            f"{BACKEND_URL}/api/article/get_article/{article_id}",
            timeout=8,
        )
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        st.warning(f"Cannot reach backend: {e}")
    return None


def api_rag_chat(question: str, article_id: str = None):
    payload = {
        "question": question,
        "user_id": MOCK_USER_ID,
        "article_id": article_id,
    }
    try:
        r = requests.post(f"{BACKEND_URL}/api/rag/chat", json=payload, timeout=30)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        return {"answer": f"Error: {e}", "citations": []}
    return {"answer": "No response from server.", "citations": []}


def api_rag_insight(article_id: str):
    payload = {"user_id": MOCK_USER_ID, "article_id": article_id}
    try:
        r = requests.post(f"{BACKEND_URL}/api/rag/insight", json=payload, timeout=60)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        return {"summary": f"Error: {e}", "key_points": [], "related": []}
    return {}


# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════


def init_state():
    defaults = {
        "page": "home",
        "article_id": None,
        "chat_open": False,
        "chat_messages": [],
        "insights": None,
        "articles_cache": None,
        "article_cache": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def go_home():
    st.session_state.page = "home"
    st.session_state.article_id = None
    st.session_state.insights = None
    st.session_state.chat_messages = []
    st.session_state.chat_open = False


def go_article(article_id: str):
    st.session_state.page = "article"
    st.session_state.article_id = article_id
    st.session_state.insights = None
    st.session_state.chat_messages = []


# ══════════════════════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════════════════════


def inject_css():
    # DO NOT INDENT the HTML/CSS inside these quotes! 
    # If you do, Streamlit will render it as a text block again.
    st.markdown(
"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Serif+4:opsz,wght@8..60,300;8..60,400;8..60,600&display=swap');

/* ── Global Font & Color Overrides ── */
html, body, [class*="css"], .stApp, .stMarkdown p, h1, h2, h3, h4, h5, h6 { 
    font-family: 'Source Serif 4', Georgia, serif !important; 
    color: #1A1410 !important; 
}

.stApp { background: #F5F0E8 !important; }
.block-container { padding: 1rem 2rem 4rem !important; max-width: 100% !important; }
[data-testid="stHeader"]     { display: none !important; }
[data-testid="stToolbar"]    { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── Sidebar (chat panel) ── */
[data-testid="stSidebar"] {
    background: #1A1410 !important;
    min-width: 340px !important; max-width: 340px !important;
}
[data-testid="stSidebar"] * { color: #F5F0E8 !important; }
[data-testid="stSidebar"] .stTextInput input {
    background: #2A2018 !important;
    border: 1px solid #3E3020 !important;
    border-radius: 20px !important;
    color: #F5F0E8 !important;
    font-family: 'Source Serif 4', serif !important;
    font-size: 13px !important;
    padding: 8px 16px !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: #C0392B !important;
    color: white !important;
    border-radius: 20px !important;
    border: none !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    padding: 8px 20px !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #A93226 !important;
}

/* ── All main-area buttons invisible (used as nav triggers) ── */
.main .stButton > button {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    color: transparent !important;
    font-family: inherit !important;
    font-size: 0 !important;
    box-shadow: none !important;
    cursor: pointer !important;
    width: 100% !important;
    text-align: left !important;
    opacity: 0 !important;
    height: auto !important;
}
.main .stButton > button:hover,
.main .stButton > button:focus,
.main .stButton > button:active {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    opacity: 0 !important;
}

/* ── Topnav strip ── */
.topnav {
    background: #FFFFFF;
    border-bottom: 1px solid #D4C9B0;
    padding: 14px 2rem;
    margin: -1rem -2rem 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
}
.logo {
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    font-weight: 900;
    color: #1A1410 !important;
    letter-spacing: -0.5px;
    flex-shrink: 0;
}
.search-box {
    flex: 1;
    max-width: 300px;
}
.search-box input {
    width: 100%;
    padding: 8px 14px;
    border: 1px solid #D4C9B0;
    border-radius: 4px;
    font-size: 13px;
    background: #F5F0E8;
}
.nav-cats {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #999 !important;
    flex: 1;
    text-align: center;
}
.nav-actions {
    display: flex;
    gap: 16px;
    align-items: center;
    flex-shrink: 0;
}
.nav-link {
    font-size: 13px;
    font-weight: 700;
    color: #1A1410 !important;
    text-decoration: none;
    cursor: pointer;
}
.nav-btn {
    padding: 8px 20px;
    border-radius: 4px;
    border: none;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
}
.nav-btn-primary {
    background: #C0392B;
    color: white !important;
}
.nav-btn-primary:hover {
    background: #A93226;
}
.live-badge {
    font-size: 11px;
    color: #BBB !important;
}

/* ── Cards ── */
.nd-card {
    background: white;
    border-radius: 6px;
    overflow: hidden;
    height: 100%;
    transition: box-shadow .2s, transform .2s;
    cursor: pointer;
    border: 1px solid #EAEAEA;
}
.nd-card:hover {
    box-shadow: 0 8px 32px rgba(0,0,0,.13);
    transform: translateY(-2px);
}
.nd-card-body {
    padding: 16px 18px 20px;
}
.nd-cat {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #C0392B !important;
    margin-bottom: 8px;
}
.nd-title {
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    color: #1A1410 !important;
    line-height: 1.3;
    margin-bottom: 10px;
}
.nd-blurb {
    font-size: 13px;
    color: #666 !important;
    line-height: 1.65;
}
.nd-meta {
    font-size: 11px;
    color: #BBB !important;
    margin-top: 10px;
}
.nd-readbtn {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #C0392B !important;
    border-bottom: 1.5px solid #C0392B;
    padding-bottom: 1px;
    display: inline-block;
    margin-top: 14px;
}

/* ── Article ── */
.art-cat {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #C0392B !important;
    margin-bottom: 14px;
}
.art-h1 {
    font-family: 'Playfair Display', serif;
    font-size: 42px;
    font-weight: 900;
    color: #1A1410 !important;
    line-height: 1.15;
    margin-bottom: 16px;
}
.art-deck {
    font-size: 18px;
    color: #444 !important;
    line-height: 1.7;
    font-style: italic;
    margin-bottom: 20px;
}
.art-meta {
    font-size: 11px;
    color: #BBB !important;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
.art-rule {
    border: none;
    border-top: 2.5px solid #1A1410;
    width: 60px;
    margin: 20px 0;
}
.art-body {
    font-size: 17px;
    color: #2A2420 !important;
    line-height: 1.9;
}

/* ── AI Panel ── */
.aip {
    background: #1A1410;
    border-radius: 10px;
    padding: 26px 20px;
    color: #F5F0E8 !important;
}
.aip-head {
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 6px;
    color: #F5F0E8 !important;
}
.aip-badge {
    display: inline-block;
    background: #C0392B;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 3px 9px;
    border-radius: 2px;
    margin-bottom: 20px;
    color: white !important;
}
.aip-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #C0392B !important;
    margin: 18px 0 9px;
}
.aip-text {
    font-size: 13.5px;
    color: #C8BFA8 !important;
    line-height: 1.75;
}
.kp {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    margin-bottom: 9px;
}
.kp-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #C0392B;
    flex-shrink: 0;
    margin-top: 7px;
}
.kp-txt {
    font-size: 13px;
    color: #C8BFA8 !important;
    line-height: 1.6;
}
.rel {
    border-top: 1px solid #2A2018;
    padding: 11px 0;
}
.rel-cat {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #C0392B !important;
    margin-bottom: 4px;
}
.rel-ttl {
    font-family: 'Playfair Display', serif;
    font-size: 13px;
    line-height: 1.4;
    color: #F5F0E8 !important;
}
.rel-sc {
    font-size: 11px;
    color: #888 !important;
    margin-top: 2px;
}

/* ── Section divider ── */
.s-hr {
    border: none;
    border-top: 1px solid #D4C9B0;
    margin: 32px 0 26px;
}
.s-heading {
    font-family: 'Playfair Display', serif;
    font-size: 26px;
    font-weight: 700;
    color: #1A1410 !important;
    margin-bottom: 18px;
}

/* ── Chat Sidebar Messages ── */
.cmsg-ai {
    background: #2A2018;
    border-radius: 12px 12px 12px 2px;
    padding: 9px 13px;
    font-size: 13px;
    line-height: 1.6;
    margin-bottom: 8px;
    color: #F5F0E8 !important;
    word-wrap: break-word;
    max-width: 85%;
}
.cmsg-usr {
    background: #C0392B;
    border-radius: 12px 12px 2px 12px;
    padding: 9px 13px;
    font-size: 13px;
    line-height: 1.6;
    margin-bottom: 8px;
    text-align: right;
    color: white !important;
    margin-left: auto;
    word-wrap: break-word;
    max-width: 85%;
}

/* ── Refresh / back buttons ── */
div[data-testid="column"]:has(button[key="refresh_btn"]) .stButton > button,
div[data-testid="column"]:has(button[key="back_btn"]) .stButton > button {
    color: #888 !important;
    font-color: 
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    padding: 6px 0 !important;
    border-bottom: 1px solid #D4C9B0 !important;
    width: auto !important;
}

::-webkit-scrollbar {
    width: 4px;
}
::-webkit-scrollbar-thumb {
    background: #C0392B;
    border-radius: 3px;
}
::-webkit-scrollbar-track {
    background: #E8E0D0;
}
/* Make sidebar citation buttons attach cleanly to their cards */
[data-testid="stSidebar"] .stButton > button {
    border-radius: 0 0 8px 8px !important; /* Flat on top, rounded on bottom */
    margin-bottom: 12px !important;
}
/* Re-round the main chat input button if it gets affected */
[data-testid="stSidebar"] .stChatInputContainer .stButton > button {
    border-radius: 12px !important;
}
</style>
""",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  NAV BAR
# ══════════════════════════════════════════════════════════════════════════════

CATEGORIES = ["LATEST", "WORLD", "SPORTS", "CULTURE", "WELLNESS", "ECONOMY"]


def render_nav():
    st.markdown(
        f"""
    <div class="topnav">
        <div class="search-box">
            <input type="text" placeholder="Search" />
        </div>
        <div class="logo">the news dispatch.</div>
        <div class="nav-actions">
            <span class="nav-link">Sign in</span>
            <button class="nav-btn nav-btn-primary">Subscribe</button>
        </div>
    </div>
    <div style="background:#FFFFFF;border-bottom:1px solid #D4C9B0;padding:12px 2rem;margin:-1rem -2rem 0 -2rem;display:flex;justify-content:center;gap:32px;">
        <span style="font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#1A1410;cursor:pointer;">LATEST</span>
        <span style="font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#999;cursor:pointer;">WORLD</span>
        <span style="font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#999;cursor:pointer;">SPORTS</span>
        <span style="font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#999;cursor:pointer;">CULTURE</span>
        <span style="font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#999;cursor:pointer;">WELLNESS</span>
        <span style="font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#999;cursor:pointer;">ECONOMY</span>
    </div>
    """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  HOME PAGE
# ══════════════════════════════════════════════════════════════════════════════


def render_home():
    if st.session_state.articles_cache is None:
        with st.spinner("Loading latest stories…"):
            st.session_state.articles_cache = api_get_articles(20) or []

    articles = st.session_state.articles_cache

    st.markdown('<div class="pw">', unsafe_allow_html=True)
    st.markdown(
        """
    <div style="padding:36px 0 20px;">
        <p style="font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#C0392B;margin-bottom:8px;">Latest</p>
        <h2 style="font-family:'Playfair Display',serif;font-size:34px;font-weight:900;color:#1A1410;margin:0 0 4px;">Today's Top Stories</h2>
        <p style="font-size:14px;color:#AAA;margin:0;">Curated news · AI insights on every article</p>
    </div>
    <hr class="section-hr" />
    """,
        unsafe_allow_html=True,
    )

    if not articles:
        st.warning(
            "No articles returned. Make sure your FastAPI server is running on localhost:8000."
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Hero row — first 3
    hero_cols = st.columns(3, gap="medium")
    for i, (col, art) in enumerate(zip(hero_cols, articles[:3])):
        with col:
            _article_card(art, i, hero=True)

    # Secondary grid — rest in rows of 4
    rest = articles[3:]
    if rest:
        st.markdown('<hr class="section-hr" />', unsafe_allow_html=True)
        st.markdown(
            '<p style="font-family:\'Playfair Display\',serif;font-size:26px;font-weight:700;color:#1A1410;margin-bottom:20px;">More Stories</p>',
            unsafe_allow_html=True,
        )
        for row_start in range(0, len(rest), 4):
            row = rest[row_start : row_start + 4]
            row_cols = st.columns(len(row), gap="medium")
            for j, (col, art) in enumerate(zip(row_cols, row)):
                with col:
                    _article_card(art, 3 + row_start + j)
            st.write("")

    st.markdown("</div>", unsafe_allow_html=True)


def _article_card(art: dict, index: int, hero: bool = False):
    img_h  = "250px" if hero else "195px"
    t_size = "21px"  if hero else "17px"
    img    = _safe_image(art, index)
    cat    = art.get("category") or art.get("source") or "NEWS"
    title  = art.get("title", "Untitled")
    blurb  = (art.get("description") or art.get("summary") or art.get("content") or "")[:180]
    author = art.get("author") or art.get("source") or ""
    date   = art.get("created_at") or art.get("date") or ""
    art_id = str(art.get("article_id") or art.get("id") or "")

    st.markdown(
        f"""
    <div class="nd-card" style="margin-bottom:6px;">
        <img src="{img}" style="height:{img_h};" />
        <div class="nd-body">
            <div class="nd-cat">{str(cat).upper()}</div>
            <div class="nd-title" style="font-size:{t_size};">{title}</div>
            <div class="nd-blurb">{blurb}{"…" if len(blurb)==180 else ""}</div>
            <div class="nd-meta">{str(author).upper()} {"· "+str(date) if date else ""}</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Invisible button overlay for card navigation
    if art_id:
        st.button(
            "Read", 
            key=f"go_{art_id}_{index}", 
            on_click=go_article,
            args=(art_id,),
            use_container_width=True
        )
    else:
        st.caption("No article ID")


# ══════════════════════════════════════════════════════════════════════════════
#  ARTICLE PAGE
# ══════════════════════════════════════════════════════════════════════════════


def render_article():
    art_id = st.session_state.article_id

    if art_id not in st.session_state.article_cache:
        with st.spinner("Loading article…"):
            st.session_state.article_cache[art_id] = api_get_article(art_id)

    art = st.session_state.article_cache.get(art_id)

    st.markdown('<div class="pw">', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("← Back to Home", key="back_btn"):
            go_home()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    if not art:
        st.error("Article not found or API unavailable.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    cat    = art.get("category") or art.get("source") or "NEWS"
    title  = art.get("title", "Untitled")
    blurb  = art.get("description") or art.get("summary") or ""
    author = art.get("author") or "John Cena"
    date   = art.get("created_at") or art.get("date") or ""
    body   = art.get("content") or blurb or "No content available."
    img    = _safe_image(art, 0)

    # Adjusted column ratio for better balance
    left, right = st.columns([1.6, 1], gap="large")

    # ── Article body ─────────────────────────────────────────────────────
    with left:
        # NOTICE: The HTML below is flush against the left margin. 
        # Do not indent the <div> tags, or Markdown will break it again!
        st.markdown(f"""
<div style="padding:28px 0 0;">
<div class="art-cat">{str(cat).upper()}</div>
<h1 class="art-h1">{title}</h1>
{"<p class='art-deck'>"+blurb+"</p>" if blurb else ""}
<div class="art-meta">
{"By " + str(author).upper() if author else ""}
{"&nbsp;·&nbsp;" + str(date) if date else ""}
</div>
<hr class="art-rule" />
</div>
<img class="art-hero" src="{img}" />
<div class="art-body">{body}</div>
<div style="display:flex;gap:16px;margin-top:20px;padding-top:24px;border-top:1px solid #D4C9B0;align-items:center;">
<span style="font-size:11px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#999;">Share</span>
<span style="font-size:18px;">𝕏</span>
<span style="font-size:18px;">𝕗</span>
<span style="font-size:18px;">in</span>
</div>
""", unsafe_allow_html=True)

    # ── AI panel ─────────────────────────────────────────────────────────
    with right:
        # Added a slight margin to push the panel down so it aligns nicely with the text
        st.markdown('<div style="margin-top: 28px;"></div>', unsafe_allow_html=True)
        _ai_panel(art_id)

    st.markdown("</div>", unsafe_allow_html=True)


def _ai_panel(art_id: str):
    if st.session_state.insights is None:
        with st.spinner("✦ Gathering AI insights…"):
            st.session_state.insights = api_rag_insight(art_id) or {}

    ins = st.session_state.insights

    # 1. Safely extract and sanitize the text. 
    # Replacing \n with <br> ensures Streamlit doesn't break it into markdown code blocks.
    raw_summary = ins.get("summary") or ins.get("answer") or "Summary not available."
    summary = str(raw_summary).replace("\n", "<br><br>")

    kps = ins.get("insights") or []
    related = ins.get("related") or []

    # 2. Build the Key Points and Related HTML strings
    kps_html = "".join(
        f'<div class="kp"><div class="kp-dot"></div><div class="kp-txt">{str(kp)}</div></div>'
        for kp in kps
    )
    
    rel_html = "".join(
        f"""<div class="rel"><div class="rel-cat">{str(r.get('category','NEWS')).upper()}</div><div class="rel-ttl">{str(r.get('title',''))}</div><div class="rel-sc">Relevance {int(float(r.get('score',0))*100)}%</div></div>"""
        for r in related
    )

    # 3. Conditionally create the sections
    kps_section = f"<div class='aip-label' style='margin-top:22px;'>🔑 Key Points</div>{kps_html}" if kps else ""
    rel_section = f"<div class='aip-label' style='margin-top:26px;'>🔗 Related Coverage</div>{rel_html}" if related else ""

    # 4. CRITICAL: Assemble everything into one continuous string. 
    # Do NOT add line breaks or indentation in this f-string!
    final_html = f"""<div class="aip"><div class="aip-head">AI Insights</div><span class="aip-badge">✦ Powered by RAG</span><div class="aip-label">📄 Summary</div><div class="aip-text">{summary}</div>{kps_section}{rel_section}</div>"""

    # 5. Render the HTML safely
    st.markdown(final_html, unsafe_allow_html=True)

    st.write("")
    if st.button("↻ Refresh Insights", key="refresh_ins"):
        st.session_state.insights = None
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  CHAT BUBBLE
# ══════════════════════════════════════════════════════════════════════════════


def _toggle_chat():
    """Callback to toggle chat open/closed state."""
    st.session_state.chat_open = not st.session_state.chat_open

def render_chat():
    article_id = st.session_state.article_id

    ctx_label = "Article assistant" if article_id else "News assistant"
    ctx_sub = (f"Article · {str(article_id)[:8]}…") if article_id else "Global · all coverage"

    with st.sidebar:
        # Header
        st.markdown(f"""
        <div style="padding-bottom: 20px; border-bottom: 1px solid #3E3020; margin-bottom: 20px;">
            <h3 style="font-family: 'Playfair Display', serif; font-size: 20px; font-weight: 700; color: #F5F0E8 !important; margin: 0 0 4px 0;">{ctx_label}</h3>
            <p style="font-size: 12px; color: #BBB !important; margin: 0; letter-spacing: 0.5px;">{ctx_sub}</p>
        </div>
        """, unsafe_allow_html=True)

        # Message Container
        msg_container = st.container(height=550, border=False)
        with msg_container:
            if not st.session_state.chat_messages:
                greeting = (
                    "📰 Ask me anything about this article!"
                    if article_id
                    else "👋 Hi! Ask me anything across our news coverage."
                )
                st.markdown(f'<div class="cmsg-ai">{greeting}</div>', unsafe_allow_html=True)
            else:
                # Loop through messages using enumerate so we have a unique index
                for msg_idx, m in enumerate(st.session_state.chat_messages):
                    css_class = "cmsg-usr" if m["role"] == "user" else "cmsg-ai"
                    safe_content = m["content"].replace("<", "&lt;").replace(">", "&gt;")
                    st.markdown(f'<div class="{css_class}">{safe_content}</div>', unsafe_allow_html=True)
                    
                    # ── NEW: Render Citation Cards ──
                    if m.get("citations"):
                        st.markdown('<p style="font-size: 10px; font-weight: 700; color: #888; text-transform: uppercase; margin: 8px 0 4px 8px; letter-spacing: 1px;">Sources</p>', unsafe_allow_html=True)
                        
                        for cit_idx, cit in enumerate(m["citations"]):
                            # Extract data (handle variations in your backend's keys)
                            c_id = cit.get("article_id") or cit.get("Article_ID") or ""
                            c_title = cit.get("title") or "Related Article"
                            c_cat = cit.get("category") or "SOURCE"
                            
                            # Draw the visual card
                            st.markdown(f"""
                            <div style="background: #2A2018; border: 1px solid #3E3020; border-radius: 8px 8px 0 0; padding: 12px; margin-bottom: -15px; position: relative; z-index: 1;">
                                <div style="font-size: 9px; color: #C0392B; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">{c_cat}</div>
                                <div style="font-size: 12px; color: #F5F0E8; font-family: 'Playfair Display', serif; line-height: 1.3;">{c_title}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Place the button underneath. Streamlit will apply our red sidebar button CSS to this!
                            if c_id:
                                st.button(
                                    "Read Full Story →", 
                                    key=f"chat_cit_{c_id}_{msg_idx}_{cit_idx}", 
                                    on_click=go_article, 
                                    args=(c_id,), 
                                    use_container_width=True
                                )

        # Native Streamlit Chat Input pinned to the bottom
        q = st.chat_input("Ask a question…")
        if q:
            st.session_state.chat_messages.append({"role": "user", "content": q.strip()})
            st.rerun()

    # Handle the API call outside the sidebar rendering logic to avoid UI freezing
    if st.session_state.chat_messages and st.session_state.chat_messages[-1]["role"] == "user":
        with st.sidebar:
            with st.spinner("Thinking…"):
                last_q = st.session_state.chat_messages[-1]["content"]
                resp = api_rag_chat(last_q, article_id)
            
            # Safely extract the answer AND citations
            answer = (resp or {}).get("answer", "No response.")
            citations = (resp or {}).get("citations", [])
            
            # Save BOTH to the chat history
            st.session_state.chat_messages.append({
                "role": "assistant", 
                "content": answer,
                "citations": citations  # <-- Saving citations here so they persist!
            })
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════


def main():
    init_state()
    inject_css()
    render_nav()

    if st.session_state.page == "home":
        render_home()
    elif st.session_state.page == "article":
        render_article()

    render_chat()


if __name__ == "__main__":
    main()