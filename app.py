import streamlit as st
import json
import os
import random
from pathlib import Path
import datetime

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NewsFlow",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ──────────────────────────────────────────────────────────────────
# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap');

# :root {
#   --ink:   #0d0d0d;
#   --paper: #f5f0e8;
#   --cream: #ede8dc;
#   --red:   #c0392b;
#   --gold:  #b8860b;
# }

# html, body, [data-testid="stAppViewContainer"] {
#   background: var(--paper) !important;
#   font-family: 'DM Sans', sans-serif;
#   color: var(--ink);
# }

# /* hide streamlit chrome */
# #MainMenu, footer, header { visibility: hidden; }
# [data-testid="stToolbar"] { display: none; }

# /* ── masthead ── */
# .masthead {
#   text-align: center;
#   border-bottom: 3px double var(--ink);
#   border-top: 3px double var(--ink);
#   padding: 12px 0 8px;
#   margin-bottom: 32px;
# }
# .masthead h1 {
#   font-family: 'Playfair Display', serif;
#   font-size: clamp(2.4rem, 6vw, 5rem);
#   font-weight: 900;
#   letter-spacing: -1px;
#   margin: 0;
#   color: var(--ink);
# }
# .masthead .tagline {
#   font-size: 0.7rem;
#   letter-spacing: 6px;
#   text-transform: uppercase;
#   color: #555;
#   margin-top: 2px;
# }
# .dateline {
#   font-size: 0.72rem;
#   letter-spacing: 2px;
#   text-transform: uppercase;
#   color: #888;
#   margin-bottom: 4px;
# }

# /* ── headline card ── */
# .card {
#   background: white;
#   border: 1px solid #ddd;
#   overflow: hidden;
#   cursor: pointer;
#   transition: box-shadow .2s, transform .2s;
#   height: 100%;
# }
# .card:hover { box-shadow: 6px 6px 0 var(--ink); transform: translate(-3px,-3px); }
# .card img  { width: 100%; height: 200px; object-fit: cover; display: block; }
# .card .no-img {
#   width: 100%; height: 200px;
#   background: linear-gradient(135deg, #1a1a1a 0%, #3a3a3a 100%);
#   display: flex; align-items: center; justify-content: center;
#   font-size: 2.5rem;
# }
# .card-body { padding: 16px; }
# .card-category {
#   font-size: 0.62rem;
#   letter-spacing: 3px;
#   text-transform: uppercase;
#   color: var(--red);
#   font-weight: 500;
#   margin-bottom: 6px;
# }
# .card-title {
#   font-family: 'Playfair Display', serif;
#   font-size: 1.1rem;
#   font-weight: 700;
#   line-height: 1.3;
#   color: var(--ink);
#   margin: 0;
# }

# /* ── hero card ── */
# .hero-card {
#   background: white;
#   border: 2px solid var(--ink);
#   overflow: hidden;
#   cursor: pointer;
#   transition: box-shadow .2s, transform .2s;
#   margin-bottom: 8px;
# }
# .hero-card:hover { box-shadow: 8px 8px 0 var(--ink); transform: translate(-4px,-4px); }
# .hero-card img { width: 100%; height: 380px; object-fit: cover; display: block; }
# .hero-card .no-img {
#   width: 100%; height: 380px;
#   background: linear-gradient(135deg, #1a1a1a 0%, #3a3a3a 100%);
#   display: flex; align-items: center; justify-content: center;
#   font-size: 4rem;
# }
# .hero-body { padding: 24px; }
# .hero-category {
#   font-size: 0.65rem;
#   letter-spacing: 4px;
#   text-transform: uppercase;
#   color: var(--red);
#   font-weight: 500;
#   margin-bottom: 8px;
# }
# .hero-title {
#   font-family: 'Playfair Display', serif;
#   font-size: clamp(1.5rem, 3vw, 2.2rem);
#   font-weight: 900;
#   line-height: 1.2;
#   color: var(--ink);
#   margin: 0 0 12px;
# }
# .hero-excerpt {
#   font-size: 0.9rem;
#   line-height: 1.6;
#   color: #444;
# }

# /* ── article page ── */
# .article-header {
#   max-width: 780px;
#   margin: 0 auto 32px;
#   border-bottom: 2px solid var(--ink);
#   padding-bottom: 24px;
# }
# .article-category {
#   font-size: 0.65rem;
#   letter-spacing: 4px;
#   text-transform: uppercase;
#   color: var(--red);
#   font-weight: 500;
#   margin-bottom: 10px;
# }
# .article-title {
#   font-family: 'Playfair Display', serif;
#   font-size: clamp(1.8rem, 4vw, 3rem);
#   font-weight: 900;
#   line-height: 1.15;
#   color: var(--ink);
#   margin: 0 0 16px;
# }
# .article-meta {
#   font-size: 0.72rem;
#   letter-spacing: 2px;
#   text-transform: uppercase;
#   color: #888;
# }
# .article-img {
#   width: 100%;
#   max-width: 780px;
#   margin: 0 auto 32px;
#   display: block;
#   border: 1px solid #ddd;
# }
# .article-content {
#   max-width: 680px;
#   margin: 0 auto;
#   font-size: 1.05rem;
#   line-height: 1.85;
#   color: #222;
# }
# .article-content p { margin-bottom: 1.4em; }

# /* ── section divider ── */
# .section-rule {
#   display: flex; align-items: center; gap: 12px;
#   margin: 28px 0 20px;
# }
# .section-rule span {
#   font-size: 0.65rem;
#   letter-spacing: 4px;
#   text-transform: uppercase;
#   color: #888;
#   white-space: nowrap;
# }
# .section-rule hr { flex: 1; border: none; border-top: 1px solid #ccc; margin: 0; }

# /* ── chatbot ── */
# .chat-fab {
#   position: fixed;
#   bottom: 28px;
#   right: 28px;
#   width: 58px;
#   height: 58px;
#   background: var(--ink);
#   border-radius: 50%;
#   display: flex;
#   align-items: center;
#   justify-content: center;
#   cursor: pointer;
#   z-index: 9999;
#   box-shadow: 0 4px 20px rgba(0,0,0,0.3);
#   font-size: 1.5rem;
#   transition: transform .2s;
# }
# .chat-fab:hover { transform: scale(1.1); }

# .chat-window {
#   position: fixed;
#   bottom: 100px;
#   right: 28px;
#   width: 360px;
#   max-height: 520px;
#   background: white;
#   border: 2px solid var(--ink);
#   box-shadow: 8px 8px 0 var(--ink);
#   display: flex;
#   flex-direction: column;
#   z-index: 9998;
#   border-radius: 2px;
# }
# .chat-header {
#   background: var(--ink);
#   color: white;
#   padding: 14px 18px;
#   font-family: 'Playfair Display', serif;
#   font-size: 1rem;
#   font-weight: 700;
#   display: flex;
#   justify-content: space-between;
#   align-items: center;
# }
# .chat-body {
#   flex: 1;
#   overflow-y: auto;
#   padding: 16px;
#   display: flex;
#   flex-direction: column;
#   gap: 12px;
#   min-height: 200px;
#   max-height: 340px;
# }
# .chat-msg-user {
#   align-self: flex-end;
#   background: var(--ink);
#   color: white;
#   padding: 10px 14px;
#   border-radius: 14px 14px 2px 14px;
#   max-width: 80%;
#   font-size: 0.88rem;
#   line-height: 1.5;
# }
# .chat-msg-bot {
#   align-self: flex-start;
#   background: var(--cream);
#   color: var(--ink);
#   border: 1px solid #ddd;
#   padding: 10px 14px;
#   border-radius: 14px 14px 14px 2px;
#   max-width: 85%;
#   font-size: 0.88rem;
#   line-height: 1.5;
# }
# .chat-msg-bot .bot-label {
#   font-size: 0.6rem;
#   letter-spacing: 2px;
#   text-transform: uppercase;
#   color: var(--red);
#   margin-bottom: 4px;
#   font-weight: 500;
# }
# .chat-footer {
#   border-top: 1px solid #eee;
#   padding: 10px 14px;
#   display: flex;
#   gap: 8px;
# }

# /* ── back button ── */
# .back-btn {
#   display: inline-flex;
#   align-items: center;
#   gap: 6px;
#   font-size: 0.72rem;
#   letter-spacing: 3px;
#   text-transform: uppercase;
#   color: #666;
#   cursor: pointer;
#   border: 1px solid #ccc;
#   padding: 6px 14px;
#   background: white;
#   transition: all .15s;
#   margin-bottom: 28px;
#   text-decoration: none;
# }
# .back-btn:hover { background: var(--ink); color: white; border-color: var(--ink); }

# </style>
# """, unsafe_allow_html=True)

# ── Global CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=DM+Sans:wght@300;400;500&display=swap');

:root {
  --ink:   #0d0d0d;
  --paper: #f5f0e8;
  --cream: #ede8dc;
  --red:   #c0392b;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background: var(--paper) !important;
  font-family: 'DM Sans', sans-serif;
  color: var(--ink);
}
[data-testid="stSidebar"] { display: none !important; }

/* hide streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
  display: none !important;
  visibility: hidden !important;
}

/* ── Override ALL Streamlit buttons ── */
.stButton > button {
  background: transparent !important;
  color: var(--red) !important;
  border: 1.5px solid var(--red) !important;
  border-radius: 0 !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.65rem !important;
  font-weight: 500 !important;
  letter-spacing: 3px !important;
  text-transform: uppercase !important;
  padding: 7px 18px !important;
  box-shadow: none !important;
  transition: background .15s, color .15s !important;
  width: auto !important;
}
.stButton > button:hover,
.stButton > button:focus {
  background: var(--red) !important;
  color: white !important;
  border-color: var(--red) !important;
  box-shadow: none !important;
}

/* back button variant */
.back-wrap .stButton > button {
  color: #666 !important;
  border-color: #aaa !important;
}
.back-wrap .stButton > button:hover {
  background: var(--ink) !important;
  color: white !important;
  border-color: var(--ink) !important;
}

/* ── masthead ── */
.masthead {
  text-align: center;
  border-bottom: 3px double var(--ink);
  border-top: 3px double var(--ink);
  padding: 12px 0 8px;
  margin-bottom: 32px;
}
.masthead h1 {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2.4rem, 6vw, 5rem);
  font-weight: 900;
  letter-spacing: -1px;
  margin: 0;
  color: var(--ink);
}
.masthead .tagline {
  font-size: 0.7rem;
  letter-spacing: 6px;
  text-transform: uppercase;
  color: #555;
  margin-top: 2px;
}
.dateline {
  font-size: 0.72rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: #888;
  margin-bottom: 4px;
}

/* ── hero ── */
.hero-card {
  background: white;
  border: 2px solid var(--ink);
  overflow: hidden;
  margin-bottom: 10px;
}
.hero-body { padding: 20px 24px 16px; }
.hero-category {
  font-size: 0.62rem; letter-spacing: 4px;
  text-transform: uppercase; color: var(--red);
  font-weight: 500; margin-bottom: 8px;
}
.hero-title {
  font-family: 'Playfair Display', serif;
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  font-weight: 900; line-height: 1.2;
  color: var(--ink); margin: 0 0 12px;
}
.hero-excerpt { font-size: 0.9rem; line-height: 1.6; color: #444; }

/* ── cards ── */
.card {
  background: white;
  border: 1px solid #ddd;
  overflow: hidden;
  margin-bottom: 4px;
}
.card-body { padding: 14px 14px 10px; }
.card-category {
  font-size: 0.58rem; letter-spacing: 3px;
  text-transform: uppercase; color: var(--red);
  font-weight: 500; margin-bottom: 5px;
}
.card-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.05rem; font-weight: 700;
  line-height: 1.3; color: var(--ink); margin: 0 0 10px;
}

/* ── section divider ── */
.section-rule {
  display: flex; align-items: center; gap: 12px;
  margin: 24px 0 18px;
}
.section-rule span {
  font-size: 0.62rem; letter-spacing: 4px;
  text-transform: uppercase; color: #888; white-space: nowrap;
}
.section-rule hr { flex: 1; border: none; border-top: 1px solid #ccc; margin: 0; }

/* ── article ── */
.article-header {
  max-width: 780px; margin: 0 auto 28px;
  border-bottom: 2px solid var(--ink); padding-bottom: 20px;
}
.article-category {
  font-size: 0.62rem; letter-spacing: 4px;
  text-transform: uppercase; color: var(--red);
  font-weight: 500; margin-bottom: 10px;
}
.article-title {
  font-family: 'Playfair Display', serif;
  font-size: clamp(1.8rem, 4vw, 2.8rem);
  font-weight: 900; line-height: 1.15;
  color: var(--ink); margin: 0 0 14px;
}
.article-meta {
  font-size: 0.7rem; letter-spacing: 2px;
  text-transform: uppercase; color: #888;
}
.article-content {
  max-width: 680px; margin: 28px auto 0;
  font-size: 1.05rem; line-height: 1.85; color: #222;
}
.article-content p { margin-bottom: 1.4em; }

/* ── floating chatbot ── */
#chat-fab {
  position: fixed; bottom: 28px; right: 28px;
  width: 56px; height: 56px;
  background: var(--ink); border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; z-index: 10000;
  box-shadow: 0 4px 20px rgba(0,0,0,.35);
  font-size: 1.4rem; user-select: none;
  transition: transform .2s, box-shadow .2s;
}
#chat-fab:hover { transform: scale(1.1); box-shadow: 0 6px 24px rgba(0,0,0,.45); }

#chat-window {
  position: fixed; bottom: 96px; right: 28px;
  width: 350px; height: 480px;
  background: white;
  border: 2px solid var(--ink);
  box-shadow: 7px 7px 0 var(--ink);
  display: none; flex-direction: column;
  z-index: 9999; border-radius: 2px;
  font-family: 'DM Sans', sans-serif;
  animation: slideUp .22s ease;
}
@keyframes slideUp {
  from { opacity:0; transform: translateY(16px); }
  to   { opacity:1; transform: translateY(0); }
}
#chat-window.open { display: flex; }

#chat-header {
  background: var(--ink); color: white;
  padding: 13px 16px;
  font-family: 'Playfair Display', serif;
  font-size: 0.95rem; font-weight: 700;
  display: flex; justify-content: space-between; align-items: center;
  flex-shrink: 0;
}
#chat-close {
  cursor: pointer; font-size: 1rem;
  opacity: .65; line-height: 1; font-family: monospace;
}
#chat-close:hover { opacity: 1; }

#chat-context {
  padding: 7px 14px;
  font-size: 0.71rem; color: #777;
  border-bottom: 1px solid #eee;
  background: #fafafa; flex-shrink: 0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

#chat-messages {
  flex: 1; overflow-y: auto;
  padding: 14px; display: flex;
  flex-direction: column; gap: 10px;
  scroll-behavior: smooth;
}
#chat-empty {
  color: #bbb; font-size: 0.82rem;
  text-align: center; margin-top: 60px;
}
.cmsg-user {
  align-self: flex-end;
  background: var(--ink); color: white;
  padding: 8px 12px;
  border-radius: 14px 14px 2px 14px;
  max-width: 82%; font-size: 0.86rem; line-height: 1.5;
}
.cmsg-bot {
  align-self: flex-start;
  background: var(--cream); border: 1px solid #ddd;
  padding: 8px 12px;
  border-radius: 14px 14px 14px 2px;
  max-width: 88%; font-size: 0.86rem; line-height: 1.5;
}
.cmsg-label {
  font-size: 0.56rem; letter-spacing: 2px;
  text-transform: uppercase; color: var(--red);
  margin-bottom: 3px; font-weight: 500;
}
.cmsg-thinking { opacity: .5; font-style: italic; }

#chat-footer {
  border-top: 1px solid #eee; padding: 10px 12px;
  display: flex; gap: 8px; flex-shrink: 0;
}
#chat-input-el {
  flex: 1; border: 1px solid #ddd;
  padding: 8px 12px; font-size: 0.86rem;
  font-family: 'DM Sans', sans-serif;
  outline: none; border-radius: 2px;
  background: var(--paper); color: var(--ink);
}
#chat-input-el:focus { border-color: var(--ink); }
#chat-send-btn {
  background: var(--ink); color: white;
  border: none; padding: 8px 14px;
  cursor: pointer; font-size: 0.9rem;
  border-radius: 2px;
  transition: opacity .15s;
}
#chat-send-btn:hover { opacity: .7; }
#chat-powered {
  font-size: 0.57rem; letter-spacing: 1px;
  color: #ccc; text-align: center;
  padding: 4px 0 8px; flex-shrink: 0;
}
</style>
""", unsafe_allow_html=True)

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