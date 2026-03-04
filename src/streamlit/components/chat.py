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