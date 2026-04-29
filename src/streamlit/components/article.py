import streamlit as st

from helper import nav, strip_source
from api.api import get_article_by_id, get_image

# ── PAGE: ARTICLE ─────────────────────────────────────────────────────────────
def render_article():
    article_id = st.session_state.current_article_id
    if not article_id:
        nav("home"); st.rerun(); return

    art = get_article_by_id(article_id=article_id)

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
            nav("chat", article_id=article_id); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    imgs_objs = get_image(art["article_id"])
    imgs = [img["image_base64"] for img in imgs_objs]
    title   = strip_source(art["title"])

    st.markdown(f"""
    <div class="article-header">
      <div class="article-kicker">News</div>
      <div class="article-title">{title}</div>
      <div class="article-meta">NewsFlow · AI Curated</div>
    </div>
    """, unsafe_allow_html=True)

    # if imgs:
    #     col, _ = st.columns([2, 1])
    #     with col:
    #         st.image(str(imgs[0]), use_container_width=True)

    # content    = art.get("content", "").strip()
    # paras      = [p.strip() for p in content.split("\n") if p.strip()]
    # html_paras = "".join(f"<p>{p}</p>" for p in paras)
    # st.markdown(f'<div class="article-content">{html_paras}</div>', unsafe_allow_html=True)
    # st.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)
    # 2. Multi-Image Rendering Logic
    if imgs:
        num_imgs = len(imgs)
        
        if num_imgs == 1:
            # Single image: use a focused column
            # Centering image
            left_co, cent_co,last_co = st.columns(3)
            with cent_co:
                st.image(str(imgs[0]), use_container_width=True, caption=art["title"])
        
        else:
            # Multiple images: Create a grid (max 2 columns)
            rows = (num_imgs + 1) // 2
            for i in range(rows):
                cols = st.columns(2)
                for j in range(2):
                    idx = i * 2 + j
                    if idx < num_imgs:
                        with cols[j]:
                            st.image(str(imgs[idx]), use_container_width=True)

    # 3. Content Rendering
    content    = art.get("content", "").strip()
    paras = [p.strip() for p in content.split("\n") if p.strip()]
    html_paras = "".join(f"<p>{p}</p>" for p in paras)
    st.markdown(f'<div class="article-content">{html_paras}</div>', unsafe_allow_html=True)
    
    # 4. Footer Spacer
    st.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)