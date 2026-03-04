import streamlit as st
import datetime

from api.api import get_articles, get_image
from helper import no_img_placeholder, strip_source, short_title, nav

# ── PAGE: HOME ────────────────────────────────────────────────────────────────
def render_home():
    today    = datetime.date.today()
    date_str = today.strftime(f"%A, %B {today.day}, %Y")

    st.markdown(f"""
    <div class="masthead">
      <div class="dateline">{date_str}</div>
      <h1>RAGNews</h1>
      <div class="tagline">AI-Powered · Curated · Intelligent</div>
    </div>
    """, unsafe_allow_html=True)

    if "selected_articles" not in st.session_state:
        articles = get_articles()
        st.session_state.selected_articles = articles

    articles = st.session_state.selected_articles
    if not articles:
        st.warning("No articles found. Add JSON files to `data/raw_news/`.")
        return

    # Can be better with recommender.
    hero = articles[0]
    rest = articles[1:]

    # ── Hero ──
    imgs = get_image(hero["id"])
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    if imgs:
        st.image(str(imgs[0]["image_base64"]), use_container_width=True)
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
        nav("article", hero["id"])
        st.rerun()

    # ── More Stories ──
    st.markdown('<div class="section-rule"><hr/><span>More Stories</span><hr/></div>',
                unsafe_allow_html=True)

    cols = st.columns(3)
    for i, art in enumerate(rest[:6]):
        with cols[i % 3]:
            imgs = get_image(art["id"])
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if imgs:
                st.image(str(imgs[0]["image_base64"]), use_container_width=True)
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
                nav("article", art["id"])
                st.rerun()

if __name__ == "__main__":
    articles = get_articles()
    print(articles)
