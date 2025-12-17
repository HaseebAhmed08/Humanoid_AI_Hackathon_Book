# Research: Physical AI & Humanoid Robotics Hackathon Project

**Feature**: 001-hackathon-project-setup
**Date**: 2025-12-16
**Status**: Complete

---

## Research Tasks Completed

### 1. Docusaurus 3.x Best Practices

**Decision**: Use Docusaurus 3.x with TypeScript configuration

**Rationale**:
- Native MDX 3 support for interactive components
- Built-in search (Algolia or local)
- Excellent code syntax highlighting (Prism)
- Easy sidebar configuration
- React 18 support for custom components

**Alternatives Considered**:
- VitePress: Faster builds but less React ecosystem integration
- GitBook: Hosted solution, less customizable
- Nextra: Good but smaller community

**Key Findings**:
- Use `@docusaurus/preset-classic` for standard features
- Swizzle `DocItem` component for personalization injection
- Use `docusaurus-plugin-content-docs` for chapter organization

---

### 2. BetterAuth Integration Pattern

**Decision**: BetterAuth with email/password + optional OAuth

**Rationale**:
- Simple API for hackathon timeline
- Built-in session management
- Works with PostgreSQL (Neon)
- TypeScript-first design

**Alternatives Considered**:
- Auth.js (NextAuth): Requires Next.js, not Docusaurus-native
- Clerk: Paid service, overkill for hackathon
- Firebase Auth: Google lock-in

**Key Findings**:
- Use `@better-auth/client` in Docusaurus
- Backend validates tokens via `@better-auth/server`
- Store sessions in Neon PostgreSQL
- Profile data stored in separate `user_profiles` table

---

### 3. RAG Architecture with Qdrant

**Decision**: Qdrant Cloud + OpenAI Embeddings + FastAPI

**Rationale**:
- Qdrant has free tier sufficient for hackathon
- OpenAI `text-embedding-3-small` is cost-effective
- FastAPI async support for concurrent requests

**Alternatives Considered**:
- Pinecone: More expensive, similar features
- Chroma: Local-first, harder to deploy
- Weaviate: More complex setup

**Key Findings**:
- Chunk chapters by heading (H2/H3 sections)
- Embed each chunk with metadata (chapter_id, section_title)
- Store 300-500 token chunks for optimal retrieval
- Use cosine similarity for search
- Return top 3-5 chunks as context

**Embedding Strategy**:
```python
# Chunk structure
{
    "id": "module-1-chapter-2-section-3",
    "text": "ROS 2 nodes are...",
    "metadata": {
        "module": "Module 1: ROS Foundations",
        "chapter": "Understanding Nodes",
        "section": "Node Lifecycle",
        "url": "/docs/module-1-ros/nodes#lifecycle"
    }
}
```

---

### 4. Translation Service Architecture

**Decision**: On-demand translation via Claude/GPT API with caching

**Rationale**:
- Real-time translation allows content updates without re-translation
- Caching reduces API costs
- Preserves technical terms automatically

**Alternatives Considered**:
- Pre-translate all content: High upfront cost, stale translations
- Google Translate API: Poor technical term handling
- Community translations: Too slow for hackathon

**Key Findings**:
- Use Claude or GPT-4 for translation
- Cache translations in PostgreSQL (`translations` table)
- Invalidate cache on content hash change
- System prompt preserves technical terms in English brackets

**Translation Prompt Template**:
```
Translate the following technical content to Urdu.
Rules:
1. Keep technical terms in English with Urdu brackets: (ROS Node)
2. Preserve all Markdown formatting
3. Maintain code blocks unchanged
4. Use formal Urdu suitable for education

Content:
{chapter_content}
```

---

### 5. Personalization Logic

**Decision**: Server-side personalization rules with client-side rendering

**Rationale**:
- Keeps personalization logic centralized
- Frontend receives pre-filtered content variants
- Scales better than client-side filtering

**Alternatives Considered**:
- Client-side only: Exposes all content variants, larger bundle
- Hybrid: Complex state management
- Pre-rendered variants: Storage explosion

**Key Findings**:
- Store personalization rules in JSON config
- Backend `/api/personalize` endpoint returns content variant
- Frontend MDX supports conditional rendering with custom components

**Personalization Rules Schema**:
```json
{
  "rules": [
    {
      "condition": {"has_nvidia_gpu": false},
      "action": "hide",
      "selector": ".isaac-sim-content"
    },
    {
      "condition": {"coding_level": "beginner"},
      "action": "show",
      "selector": ".beginner-explanation"
    }
  ]
}
```

---

### 6. Neon PostgreSQL Schema Design

**Decision**: Normalized schema with separate tables for users, profiles, sessions

**Rationale**:
- BetterAuth manages `users` and `sessions` tables
- Custom `user_profiles` table for learning context
- `translations` table for caching

**Key Findings**:
- Use Neon's serverless driver for edge compatibility
- Connection pooling via Neon's built-in pooler
- Migrations via Drizzle ORM or raw SQL

---

### 7. Deployment Strategy

**Decision**: Vercel (frontend) + Railway/Render (backend) + Qdrant Cloud

**Rationale**:
- Vercel has excellent Docusaurus support
- Railway/Render have free tiers for FastAPI
- Qdrant Cloud has 1GB free tier

**Alternatives Considered**:
- All on Vercel: FastAPI support limited
- Docker on single VPS: More setup, less scalable
- AWS/GCP: Overkill for hackathon

**Key Findings**:
- Frontend: `vercel deploy`
- Backend: Railway with `requirements.txt`
- Environment variables managed per platform
- CORS configured for cross-origin API calls

---

## Resolved Clarifications

| Original Unknown | Resolution | Source |
|-----------------|------------|--------|
| Auth method | BetterAuth with email/password | Constitution + research |
| Vector DB choice | Qdrant Cloud (free tier) | Constitution + research |
| Translation approach | On-demand with Claude API + caching | Cost/quality analysis |
| Personalization delivery | Server-side rules, client rendering | Performance analysis |
| Deployment platform | Vercel + Railway + Qdrant Cloud | Free tier availability |

---

## Technology Decisions Summary

| Category | Decision | Confidence |
|----------|----------|------------|
| Frontend Framework | Docusaurus 3.x | High |
| Backend Framework | FastAPI | High |
| Authentication | BetterAuth | High |
| Database | Neon PostgreSQL | High |
| Vector Store | Qdrant Cloud | High |
| Embeddings | OpenAI text-embedding-3-small | High |
| LLM (Chat) | OpenAI GPT-4o-mini | High |
| LLM (Translation) | Claude 3.5 Sonnet | High |
| Deployment | Vercel + Railway | Medium |

---

## Next Steps

1. Proceed to Phase 1: Generate `data-model.md`
2. Generate API contracts in `contracts/`
3. Create `quickstart.md` for developer onboarding
