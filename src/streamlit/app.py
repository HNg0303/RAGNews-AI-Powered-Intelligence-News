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

# ── Global CSS ──────────────────────────────────────────────────────────────────


# ── Helpers ─────────────────────────────────────────────────────────────────────

DATA_DIR   = Path("data/raw_news")
IMAGE_DIR  = Path("data/images")

@st.cache_data
def load_all_articles():
    articles = []
    if not DATA_DIR.exists():
        # demo fallback if directory is missing entirely
        return _demo_articles()

    # walk recursively to include subfolders like CNN/, APNews/, etc.
    for root, _, files in os.walk(DATA_DIR):
        for fname in files:
            if fname.endswith(".json"):
                path = Path(root) / fname
                try:
                    with open(path, encoding="utf-8") as fp:
                        articles.append(json.load(fp))
                except Exception:
                    continue

    return articles if articles else _demo_articles()


def _demo_articles():
    return [
        {
            "id": "demo-001",
            "title": "'Golden' wins K-pop's first Grammy. Is this a breakthrough moment? | CNN",
            "content": (
                "Golden was already a global chart-dominating force, but taking home the "
                "Best Song Written for Visual Media award in Los Angeles is a milestone moment "
                "for K-pop – a genre that despite its growing influence on Western pop culture "
                "has long been considered niche.\n\n"
                "\"It does feel so miraculous in some ways. And destined in other ways…\" said "
                "Audrey Nuna, who lends her voice to a member of Huntr/x in the film.\n\n"
                "The Grammy itself went to the songwriters: EJAE, Park Hong Jun, Joong Gyu Kwak, "
                "Yu Han Lee, Hee Dong Nam, Seo Jeong Hoon and Mark Sonnenblick – the first win "
                "for any Korean songwriters or producers.\n\n"
                "It was only in 2021 that a K-pop act first earned a Grammy nomination. "
                "This year, songs released by K-pop artists received nominations in five categories."
            ),
        },
        {
            "id": "demo-002",
            "title": "Global markets rally as central banks signal pause on rate hikes | Reuters",
            "content": (
                "Stock markets across Europe and Asia climbed sharply on Thursday after "
                "officials from the Federal Reserve and the European Central Bank each signalled "
                "a pause in their respective rate-hiking cycles, offering relief to investors "
                "who had braced for further tightening.\n\n"
                "The S&P 500 futures rose 1.4 %, while the pan-European STOXX 600 added "
                "1.9 % by mid-morning trading. Bond yields fell across maturities as money "
                "markets repriced the probability of further increases lower.\n\n"
                "Analysts cautioned that the pause is conditional and could reverse quickly "
                "if inflation data surprises to the upside in coming months."
            ),
        },
        {
            "id": "demo-003",
            "title": "Scientists discover microplastics in remote Antarctic snowfall | Nature",
            "content": (
                "Researchers have detected microplastic particles in freshly fallen snow "
                "collected on the Antarctic plateau, far from any human settlement or industrial "
                "activity, according to a study published in Nature Communications.\n\n"
                "The finding suggests that atmospheric transport is capable of carrying plastic "
                "pollution to even the most isolated corners of the planet. The concentrations, "
                "while lower than those found in urban snowfall, are nonetheless significant.\n\n"
                "Lead author Dr. Lena Hoffmann called the discovery 'a sobering reminder that "
                "no ecosystem remains truly pristine.' The team called for urgent global "
                "action to reduce single-use plastics."
            ),
        },
        {
            "id": "demo-004",
            "title": "Apple unveils spatial computing headset successor with neural interface | The Verge",
            "content": (
                "Apple on Tuesday introduced the second-generation Vision platform, adding "
                "a neural-interface wristband accessory that interprets subtle finger muscle "
                "signals to allow hands-free navigation and text entry.\n\n"
                "The new headset is lighter than its predecessor, weighing 280 grams, and "
                "features a next-generation chip the company claims delivers twice the "
                "graphics performance of any previous silicon it has shipped.\n\n"
                "Priced at $2,999, the device will ship later this quarter. Analysts said "
                "the neural interface could be the most significant input paradigm shift "
                "since the touchscreen."
            ),
        },
        {
            "id": "demo-005",
            "title": "Paris unveils ambitious Seine river urban beach expansion for 2026 | Le Monde",
            "content": (
                "The Mayor of Paris announced an expanded Paris Plages programme for the "
                "summer of 2026, stretching the temporary urban beach along the Seine from "
                "the Trocadéro all the way to the Bois de Vincennes – nearly double the "
                "previous length.\n\n"
                "The initiative, first launched in 2002, will this year include outdoor "
                "cinema screenings, food markets celebrating cuisines from the city's twenty "
                "arrondissements, and free open-water swimming zones following the clean-up "
                "of the Seine completed ahead of the 2024 Olympics.\n\n"
                "Officials expect the expansion to draw over four million visitors across "
                "the six-week season."
            ),
        },
    ]


def get_image_path(article_id: str):
    folder = IMAGE_DIR / article_id
    if folder.exists():
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.gif"):
            imgs = list(folder.glob(ext))
            if imgs:
                return imgs[0]
    return None


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
if "selected_articles" not in st.session_state:
    arts = load_all_articles()
    random.shuffle(arts)
    st.session_state.selected_articles = arts[:7] if len(arts) >= 7 else arts


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

# ── PAGE: HOME ────────────────────────────────────────────────────────────────
def render_home():
    today    = datetime.date.today()
    date_str = today.strftime(f"%A, %B {today.day}, %Y")

    st.markdown(f"""
    <div class="masthead">
      <div class="dateline">{date_str}</div>
      <h1>NewsFlow</h1>
      <div class="tagline">AI-Powered · Curated · Intelligent</div>
    </div>
    """, unsafe_allow_html=True)

    articles = st.session_state.selected_articles
    if not articles:
        st.warning("No articles found. Add JSON files to `data/raw_news/`.")
        return

    hero = articles[0]
    rest = articles[1:]

    # ── Hero ──
    img_path = get_image_path(hero["id"])
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    if img_path:
        st.image(str(img_path), use_container_width=True)
    else:
        st.markdown(no_img_placeholder(340, "📰"), unsafe_allow_html=True)
    st.markdown(f"""
    <div class="hero-body">
      <div class="hero-kicker">Top Story</div>
      <div class="hero-title">{strip_source(hero['title'])}</div>
      <div class="hero-excerpt">{hero.get('content','')[:240].strip()}…</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Read full story →", key="hero_btn"):
        nav("article", hero)
        st.rerun()

    # ── More Stories ──
    st.markdown('<div class="section-rule"><hr/><span>More Stories</span><hr/></div>',
                unsafe_allow_html=True)

    cols = st.columns(3)
    for i, art in enumerate(rest[:6]):
        with cols[i % 3]:
            img_path = get_image_path(art["id"])
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if img_path:
                st.image(str(img_path), use_container_width=True)
            else:
                st.markdown(no_img_placeholder(190), unsafe_allow_html=True)
            st.markdown(f"""
            <div class="card-body">
              <div class="card-kicker">News</div>
              <div class="card-title">{strip_source(short_title(art['title'], 10))}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button("Read →", key=f"card_{i}"):
                nav("article", art)
                st.rerun()


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