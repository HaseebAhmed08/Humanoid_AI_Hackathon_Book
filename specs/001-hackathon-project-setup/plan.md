# Implementation Plan: Physical AI & Humanoid Robotics Hackathon Project

**Branch**: `001-hackathon-project-setup` | **Date**: 2025-12-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-hackathon-project-setup/spec.md`

---

## Summary

Build an educational platform for Physical AI and Humanoid Robotics consisting of:
1. **Docusaurus-based textbook** with 4 modules and 12+ chapters
2. **RAG-powered chatbot** for learning assistance using Qdrant + FastAPI
3. **User authentication** with BetterAuth for personalization
4. **Content personalization** based on user hardware/software background
5. **Urdu translation** for accessibility

Technical approach: Monorepo with separate frontend (Docusaurus) and backend (FastAPI) services, connected via REST APIs.

---

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.x, React 18.x, Node.js 20.x LTS
- Backend: Python 3.11+
- Documentation: MDX (Markdown + JSX)

**Primary Dependencies**:
- Frontend: Docusaurus 3.x, React, BetterAuth Client, ChatKit SDK
- Backend: FastAPI, Pydantic, OpenAI SDK, Qdrant Client, SQLAlchemy

**Storage**:
- Relational: Neon PostgreSQL (users, profiles, sessions)
- Vector: Qdrant Cloud (chapter embeddings for RAG)
- Content: MDX files in Git repository

**Testing**:
- Frontend: Jest + React Testing Library
- Backend: pytest + pytest-asyncio
- E2E: Playwright (optional for hackathon)

**Target Platform**: Web (responsive, mobile-friendly)

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- Page load: < 3 seconds
- Chatbot response: < 5 seconds
- Translation: < 3 seconds

**Constraints**:
- Hackathon timeline (prioritize P1-P3 features)
- No enterprise features (SSO, audit logs)
- English + Urdu only

**Scale/Scope**:
- 4 modules, 12+ chapters
- ~100 concurrent users for demo
- Single region deployment

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Multi-agent architecture | ✅ PASS | 8 agents defined with clear boundaries |
| Agent/Skill separation | ✅ PASS | Skills are reusable, agents make decisions |
| No hardcoded secrets | ✅ PASS | Using .env files and environment variables |
| Docusaurus for docs | ✅ PASS | Primary frontend framework |
| FastAPI for backend | ✅ PASS | API and RAG services |
| BetterAuth for auth | ✅ PASS | Authentication provider |
| Neon PostgreSQL | ✅ PASS | User data storage |
| Qdrant for vectors | ✅ PASS | RAG embeddings |
| Simplicity prioritized | ✅ PASS | MVP features only for hackathon |
| Beginner-friendly content | ✅ PASS | Curriculum Author responsibility |

**Gate Status**: ✅ PASSED - Proceeding to Phase 0

---

## Project Structure

### Documentation (this feature)

```text
specs/001-hackathon-project-setup/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API schemas)
│   ├── auth.yaml
│   ├── chat.yaml
│   ├── profile.yaml
│   └── translation.yaml
├── checklists/
│   └── requirements.md  # Spec validation checklist
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
# Frontend: Docusaurus Site
website/
├── docusaurus.config.ts
├── sidebars.ts
├── src/
│   ├── components/
│   │   ├── ChatWidget/
│   │   ├── TranslateButton/
│   │   ├── PersonalizeButton/
│   │   └── ProfileForm/
│   ├── pages/
│   │   ├── index.tsx
│   │   └── profile.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useChat.ts
│   │   └── usePersonalization.ts
│   └── theme/
│       └── DocItem/        # Swizzled for personalization
├── docs/
│   ├── module-1-ros/
│   │   ├── intro.mdx
│   │   ├── nodes-topics.mdx
│   │   └── ...
│   ├── module-2-simulation/
│   ├── module-3-digital-twin/
│   └── module-4-ai-brain/
└── static/

# Backend: FastAPI Services
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   ├── user.py
│   │   ├── profile.py
│   │   └── chat.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── profile.py
│   │   └── translate.py
│   ├── services/
│   │   ├── rag_service.py
│   │   ├── embedding_service.py
│   │   ├── translation_service.py
│   │   └── personalization_service.py
│   └── db/
│       ├── database.py
│       └── migrations/
├── scripts/
│   └── index_chapters.py
├── tests/
│   ├── test_auth.py
│   ├── test_chat.py
│   └── test_rag.py
├── requirements.txt
└── .env.example

# Shared
.env.example
docker-compose.yml (optional)
```

**Structure Decision**: Web application with separate `website/` (Docusaurus frontend) and `backend/` (FastAPI API) directories. This aligns with the constitution's technology stack and allows independent deployment.

---

## Agent Responsibilities by Component

| Component | Primary Agent | Supporting Agents |
|-----------|--------------|-------------------|
| `website/docs/` | Curriculum Author | ROS Systems, Sim Physics, GenAI VLA |
| `website/src/components/` | Docusaurus Builder | Personalization Agent |
| `backend/routers/auth.py` | Authentication Agent | - |
| `backend/services/rag_service.py` | RAG Engineer | - |
| `backend/routers/translate.py` | Urdu Translation Agent | - |
| All outputs | QA Agent | - |

---

## Complexity Tracking

No constitution violations detected. Architecture follows prescribed stack and principles.

---

## Implementation Phases

### Phase 0: Research (Complete)
See [research.md](./research.md)

### Phase 1: Design (Complete)
- [data-model.md](./data-model.md) - Entity definitions
- [contracts/](./contracts/) - API schemas
- [quickstart.md](./quickstart.md) - Developer setup guide

### Phase 2: Tasks (Pending)
Run `/sp.tasks` to generate implementation tasks from this plan.

---

## Architecture Decision Records

📋 **Architectural decisions detected during planning:**

1. **Monorepo vs Polyrepo** - Using monorepo for hackathon simplicity
2. **BetterAuth Integration** - Client-side with FastAPI backend validation
3. **RAG Architecture** - Qdrant Cloud for vector storage, OpenAI for embeddings

Suggest documenting: Run `/sp.adr "monorepo-architecture"` if needed.
