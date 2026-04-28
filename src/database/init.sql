-- =============================================================================
-- RAGNews — PostgreSQL Init Script
-- Run once against a fresh database:
--   psql -U postgres -d ragnews -f init.sql
-- =============================================================================

-- ── Extensions ────────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";   -- gen_random_uuid()

-- =============================================================================
-- USERS
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    user_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username   VARCHAR(100) UNIQUE,
    email      TEXT UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- ARTICLES  (heavy — fetched only when user opens an article)
-- =============================================================================
CREATE TABLE IF NOT EXISTS articles (
    article_id      TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    subtitle        TEXT,
    content         TEXT,
    image_url       TEXT,                    -- Cloudinary CDN URL
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Summarization (lazy cache)
    summary         TEXT,
    is_summarized   BOOLEAN NOT NULL DEFAULT FALSE,
    summarized_at   TIMESTAMPTZ,

    -- Sentiment
    sentiment       VARCHAR(20),             -- positive | neutral | negative
    sentiment_score FLOAT                    -- confidence 0.0 – 1.0
);

CREATE INDEX IF NOT EXISTS idx_articles_is_summarized ON articles (is_summarized);


-- =============================================================================
-- THREADS
-- =============================================================================
CREATE TABLE IF NOT EXISTS threads (
    thread_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID REFERENCES users (user_id) ON DELETE CASCADE,
    article_id TEXT REFERENCES articles (article_id) ON DELETE CASCADE,  -- CHANGED: UUID to TEXT
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- One global thread per user (article_id IS NULL)
CREATE UNIQUE INDEX IF NOT EXISTS idx_threads_user_global
    ON threads (user_id)
    WHERE article_id IS NULL;

-- One thread per user per article
CREATE UNIQUE INDEX IF NOT EXISTS idx_threads_user_article
    ON threads (user_id, article_id)
    WHERE article_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_threads_user_id    ON threads (user_id);
CREATE INDEX IF NOT EXISTS idx_threads_article_id ON threads (article_id);


-- =============================================================================
-- MESSAGES  (LangChain-compatible conversation history)
-- =============================================================================
CREATE TABLE IF NOT EXISTS messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id  UUID NOT NULL REFERENCES threads (thread_id) ON DELETE CASCADE,
    role       VARCHAR(20) NOT NULL CHECK (role IN ('human', 'ai', 'tool')),
    content    TEXT NOT NULL,

    -- Flexible metadata: citations, tool calls, token counts
    -- Example: {"citations": [...], "tool_calls": [...], "tokens": {...}}
    meta       JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_thread_id  ON messages (thread_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages (thread_id, created_at ASC);


-- =============================================================================
-- USER INTERACTIONS  (raw event log — source of truth for personalization)
-- =============================================================================
CREATE TABLE IF NOT EXISTS user_interactions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users (user_id) ON DELETE CASCADE,
    article_id  TEXT NOT NULL REFERENCES articles (article_id) ON DELETE CASCADE, -- CHANGED: UUID to TEXT
    interaction VARCHAR(20) NOT NULL CHECK (interaction IN ('click', 'qna', 'share')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_interactions_user    ON user_interactions (user_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_article ON user_interactions (article_id);


-- =============================================================================
-- USER PREFERENCES  (aggregated — refreshed async after each interaction)
-- =============================================================================
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id          UUID PRIMARY KEY REFERENCES users (user_id) ON DELETE CASCADE,
    -- {"technology": 0.8, "finance": 0.3}
    category_weights JSONB NOT NULL DEFAULT '{}',
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- HELPER FUNCTION: update updated_at automatically
-- =============================================================================
CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER set_threads_updated_at
    BEFORE UPDATE ON threads
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- FIXED TYPO: "user_pr--eferences" to "user_preferences"
CREATE OR REPLACE TRIGGER set_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences 
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();