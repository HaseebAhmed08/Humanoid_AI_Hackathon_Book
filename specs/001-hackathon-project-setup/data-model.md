# Data Model: Physical AI & Humanoid Robotics Platform

**Feature**: 001-hackathon-project-setup
**Date**: 2025-12-16
**Database**: Neon PostgreSQL + Qdrant (Vector)

---

## Entity Relationship Diagram

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   users     │────<│  user_profiles   │     │   translations  │
│  (BetterAuth)│     │                  │     │                 │
└─────────────┘     └──────────────────┘     └─────────────────┘
       │                                              │
       │                                              │
       ▼                                              │
┌─────────────┐     ┌──────────────────┐              │
│  sessions   │     │  chat_sessions   │──────────────┘
│ (BetterAuth)│     │                  │
└─────────────┘     └──────────────────┘
                           │
                           ▼
                    ┌──────────────────┐
                    │  chat_messages   │
                    │                  │
                    └──────────────────┘

Vector Store (Qdrant):
┌─────────────────────┐
│  chapter_embeddings │
│                     │
└─────────────────────┘
```

---

## PostgreSQL Entities

### 1. users (Managed by BetterAuth)

BetterAuth manages this table automatically.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| email_verified | BOOLEAN | DEFAULT false | Email verification status |
| hashed_password | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| created_at | TIMESTAMP | DEFAULT NOW() | Account creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |

---

### 2. sessions (Managed by BetterAuth)

BetterAuth manages this table automatically.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Session identifier |
| user_id | UUID | FK → users.id | Associated user |
| token | VARCHAR(255) | UNIQUE, NOT NULL | Session token |
| expires_at | TIMESTAMP | NOT NULL | Session expiration |
| created_at | TIMESTAMP | DEFAULT NOW() | Session creation time |

---

### 3. user_profiles

Stores user learning context for personalization.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Profile identifier |
| user_id | UUID | FK → users.id, UNIQUE | One profile per user |
| coding_level | ENUM | NOT NULL, DEFAULT 'beginner' | beginner, intermediate, advanced |
| has_nvidia_gpu | BOOLEAN | DEFAULT false | User has NVIDIA GPU |
| has_robot | BOOLEAN | DEFAULT false | User has physical robot |
| robot_platform | VARCHAR(50) | NULLABLE | unitree, boston_dynamics, custom, other |
| primary_interest | ENUM | DEFAULT 'both' | software, hardware, both |
| preferred_language | VARCHAR(5) | DEFAULT 'en' | en, ur |
| learning_goals | TEXT | NULLABLE | Free-form learning objectives |
| created_at | TIMESTAMP | DEFAULT NOW() | Profile creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |

**Indexes**:
- `idx_user_profiles_user_id` on `user_id`

**Validation Rules**:
- `coding_level` must be one of: beginner, intermediate, advanced
- `primary_interest` must be one of: software, hardware, both
- `preferred_language` must be one of: en, ur

---

### 4. chat_sessions

Tracks conversation threads with the chatbot.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Chat session identifier |
| user_id | UUID | FK → users.id, NULLABLE | Associated user (null for anonymous) |
| started_at | TIMESTAMP | DEFAULT NOW() | Session start time |
| last_activity | TIMESTAMP | DEFAULT NOW() | Last message time |
| context_chapter | VARCHAR(100) | NULLABLE | Current chapter being read |
| is_active | BOOLEAN | DEFAULT true | Session still active |

**Indexes**:
- `idx_chat_sessions_user_id` on `user_id`
- `idx_chat_sessions_active` on `is_active, last_activity`

---

### 5. chat_messages

Stores individual messages in chat sessions.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Message identifier |
| session_id | UUID | FK → chat_sessions.id | Parent session |
| role | ENUM | NOT NULL | user, assistant, system |
| content | TEXT | NOT NULL | Message content |
| sources | JSONB | NULLABLE | Array of source references |
| created_at | TIMESTAMP | DEFAULT NOW() | Message timestamp |

**Indexes**:
- `idx_chat_messages_session_id` on `session_id`

**Sources JSONB Structure**:
```json
[
  {
    "chapter": "Module 1: Understanding Nodes",
    "section": "Node Lifecycle",
    "url": "/docs/module-1-ros/nodes#lifecycle",
    "relevance_score": 0.89
  }
]
```

---

### 6. translations

Caches translated chapter content.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Translation identifier |
| chapter_path | VARCHAR(255) | NOT NULL | Original chapter file path |
| content_hash | VARCHAR(64) | NOT NULL | SHA-256 of original content |
| target_language | VARCHAR(5) | NOT NULL | Target language code (ur) |
| translated_content | TEXT | NOT NULL | Translated Markdown content |
| created_at | TIMESTAMP | DEFAULT NOW() | Translation creation time |
| expires_at | TIMESTAMP | NULLABLE | Cache expiration (30 days) |

**Indexes**:
- `idx_translations_lookup` on `chapter_path, target_language, content_hash` (UNIQUE)

**Cache Invalidation**:
- When `content_hash` doesn't match, translation is stale
- Expired translations (past `expires_at`) are refreshed on demand

---

## Qdrant Vector Store

### Collection: chapter_embeddings

Stores vector embeddings for RAG retrieval.

**Vector Configuration**:
- Dimensions: 1536 (OpenAI text-embedding-3-small)
- Distance: Cosine
- On-disk: false (fits in memory for hackathon scale)

**Point Structure**:
```json
{
  "id": "module-1-chapter-2-section-3",
  "vector": [0.123, -0.456, ...],
  "payload": {
    "module_id": "module-1-ros",
    "module_title": "Module 1: ROS 2 Foundations",
    "chapter_id": "nodes-topics",
    "chapter_title": "Understanding Nodes and Topics",
    "section_title": "Node Lifecycle",
    "content": "ROS 2 nodes have a defined lifecycle...",
    "url": "/docs/module-1-ros/nodes-topics#lifecycle",
    "word_count": 342,
    "difficulty": "beginner"
  }
}
```

**Payload Fields**:
| Field | Type | Description |
|-------|------|-------------|
| module_id | string | Module slug |
| module_title | string | Human-readable module name |
| chapter_id | string | Chapter slug |
| chapter_title | string | Human-readable chapter name |
| section_title | string | H2/H3 heading text |
| content | string | Raw text chunk (300-500 tokens) |
| url | string | Direct link to section |
| word_count | integer | Words in chunk |
| difficulty | string | beginner, intermediate, advanced |

---

## State Transitions

### User Profile States

```
[New User] → [Profile Incomplete] → [Profile Complete]
                    ↑                       │
                    └───────────────────────┘
                         (Profile Update)
```

### Chat Session States

```
[Created] → [Active] → [Idle] → [Expired]
              ↑   │
              └───┘
           (New Message)
```

- Active: Last activity within 30 minutes
- Idle: Last activity 30-60 minutes ago
- Expired: Last activity > 60 minutes ago (auto-close)

---

## SQL Schema

```sql
-- Enums
CREATE TYPE coding_level AS ENUM ('beginner', 'intermediate', 'advanced');
CREATE TYPE interest_type AS ENUM ('software', 'hardware', 'both');
CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');

-- User Profiles
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    coding_level coding_level NOT NULL DEFAULT 'beginner',
    has_nvidia_gpu BOOLEAN DEFAULT false,
    has_robot BOOLEAN DEFAULT false,
    robot_platform VARCHAR(50),
    primary_interest interest_type DEFAULT 'both',
    preferred_language VARCHAR(5) DEFAULT 'en',
    learning_goals TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);

-- Chat Sessions
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    started_at TIMESTAMP DEFAULT NOW(),
    last_activity TIMESTAMP DEFAULT NOW(),
    context_chapter VARCHAR(100),
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_active ON chat_sessions(is_active, last_activity);

-- Chat Messages
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role message_role NOT NULL,
    content TEXT NOT NULL,
    sources JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);

-- Translations Cache
CREATE TABLE translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_path VARCHAR(255) NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    target_language VARCHAR(5) NOT NULL,
    translated_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    UNIQUE(chapter_path, target_language, content_hash)
);

CREATE INDEX idx_translations_lookup ON translations(chapter_path, target_language, content_hash);
```

---

## Data Retention

| Entity | Retention | Deletion Trigger |
|--------|-----------|------------------|
| users | Indefinite | User request or 2 years inactivity |
| user_profiles | Tied to user | Cascade on user deletion |
| chat_sessions | 90 days | Auto-cleanup job |
| chat_messages | Tied to session | Cascade on session deletion |
| translations | 30 days | Cache expiration |
| chapter_embeddings | Indefinite | Content re-indexing |
