-- Physical AI & Humanoid Robotics Platform
-- Database Schema for Neon PostgreSQL
-- Based on data-model.md

-- =============================================================================
-- ENUMS
-- =============================================================================

-- Coding level for user profiles
CREATE TYPE coding_level AS ENUM ('beginner', 'intermediate', 'advanced');

-- Primary interest area
CREATE TYPE interest_type AS ENUM ('software', 'hardware', 'both');

-- Chat message role
CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');

-- =============================================================================
-- TABLES
-- =============================================================================

-- Note: users and sessions tables are managed by BetterAuth
-- They will be created automatically by the auth library

-- User Profiles - stores learning context for personalization
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,  -- References BetterAuth users table
    coding_level coding_level NOT NULL DEFAULT 'beginner',
    has_nvidia_gpu BOOLEAN DEFAULT false,
    has_robot BOOLEAN DEFAULT false,
    robot_platform VARCHAR(50),  -- unitree, boston_dynamics, custom, other
    primary_interest interest_type DEFAULT 'both',
    preferred_language VARCHAR(5) DEFAULT 'en',  -- en, ur
    learning_goals TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat Sessions - tracks conversation threads
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,  -- Nullable for anonymous sessions
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    context_chapter VARCHAR(100),  -- Current chapter being read
    is_active BOOLEAN DEFAULT true
);

-- Chat Messages - individual messages in sessions
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role message_role NOT NULL,
    content TEXT NOT NULL,
    sources JSONB,  -- Array of source references
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Translations Cache - caches translated chapter content
CREATE TABLE IF NOT EXISTS translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_path VARCHAR(255) NOT NULL,
    content_hash VARCHAR(64) NOT NULL,  -- SHA-256 of original content
    target_language VARCHAR(5) NOT NULL,  -- ur
    translated_content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,  -- Cache expiration (30 days)
    UNIQUE(chapter_path, target_language, content_hash)
);

-- =============================================================================
-- INDEXES
-- =============================================================================

-- User profiles
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);

-- Chat sessions
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_active ON chat_sessions(is_active, last_activity);

-- Chat messages
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created ON chat_messages(session_id, created_at);

-- Translations
CREATE INDEX IF NOT EXISTS idx_translations_lookup
    ON translations(chapter_path, target_language, content_hash);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to user_profiles
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Update last_activity on chat_sessions when message added
CREATE OR REPLACE FUNCTION update_chat_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_sessions
    SET last_activity = NOW()
    WHERE id = NEW.session_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_session_activity ON chat_messages;
CREATE TRIGGER update_session_activity
    AFTER INSERT ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_chat_session_activity();
