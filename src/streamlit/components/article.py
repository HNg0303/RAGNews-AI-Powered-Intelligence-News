import streamlit as st

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