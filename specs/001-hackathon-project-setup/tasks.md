# Tasks: Physical AI & Humanoid Robotics Hackathon Project

**Input**: Design documents from `/specs/001-hackathon-project-setup/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are NOT explicitly requested in the feature specification. Test tasks are OMITTED.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `website/` (Docusaurus)
- **Backend**: `backend/` (FastAPI)
- Paths follow plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for both frontend and backend

- [X] T001 Create project structure with `website/` and `backend/` directories per plan.md
- [X] T002 [P] Initialize Docusaurus 3.x project in website/ with TypeScript
- [X] T003 [P] Initialize FastAPI project in backend/ with Python 3.11+ virtual environment
- [X] T004 [P] Create .env.example with all required environment variables (DATABASE_URL, QDRANT_URL, OPENAI_API_KEY, ANTHROPIC_API_KEY, BETTER_AUTH_SECRET)
- [X] T005 [P] Create backend/requirements.txt with FastAPI, Pydantic, SQLAlchemy, Qdrant-client, OpenAI dependencies
- [X] T006 [P] Create website/package.json with Docusaurus, React, BetterAuth client dependencies
- [X] T007 Configure ESLint and Prettier for website/ in website/.eslintrc.js
- [X] T008 Configure Ruff linter for backend/ in backend/pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Create database connection module in backend/app/db/database.py with Neon PostgreSQL connection pooling
- [X] T010 Create SQL schema file in backend/app/db/schema.sql with enums and tables from data-model.md
- [ ] T011 Run database migrations to create user_profiles, chat_sessions, chat_messages, translations tables
- [X] T012 [P] Create base Pydantic schemas in backend/app/schemas/base.py for common response models
- [X] T013 [P] Create FastAPI application entry point in backend/app/main.py with CORS configuration
- [X] T014 [P] Create configuration module in backend/app/config.py with environment variable loading
- [X] T015 [P] Create Docusaurus configuration in website/docusaurus.config.ts with basic site metadata
- [X] T016 [P] Create sidebar configuration in website/sidebars.ts with 4 module structure
- [X] T017 Setup error handling middleware in backend/app/middleware/error_handler.py
- [X] T018 Setup logging configuration in backend/app/middleware/logging.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Browse and Read Educational Content (Priority: P1) 🎯 MVP

**Goal**: Learners can navigate and read structured educational content with syntax-highlighted code

**Independent Test**: Navigate to website, open any chapter, verify MDX content renders with syntax-highlighted code blocks

### Implementation for User Story 1

- [X] T019 [P] [US1] Create module-1-ros/ directory structure in website/docs/module-1-ros/
- [X] T020 [P] [US1] Create module-2-simulation/ directory structure in website/docs/module-2-simulation/
- [X] T021 [P] [US1] Create module-3-digital-twin/ directory structure in website/docs/module-3-digital-twin/
- [X] T022 [P] [US1] Create module-4-ai-brain/ directory structure in website/docs/module-4-ai-brain/
- [X] T023 [P] [US1] Create intro chapter placeholder in website/docs/module-1-ros/intro.mdx with frontmatter (sidebar_position, title, description)
- [X] T024 [P] [US1] Create nodes-topics chapter placeholder in website/docs/module-1-ros/nodes-topics.mdx
- [X] T025 [P] [US1] Create intro chapter placeholder in website/docs/module-2-simulation/intro.mdx
- [X] T026 [P] [US1] Create intro chapter placeholder in website/docs/module-3-digital-twin/intro.mdx
- [X] T027 [P] [US1] Create intro chapter placeholder in website/docs/module-4-ai-brain/intro.mdx
- [X] T028 [US1] Configure Prism syntax highlighting for Python, YAML, XML, bash in website/docusaurus.config.ts
- [X] T029 [US1] Create homepage component in website/src/pages/index.tsx with module navigation
- [X] T030 [US1] Add reading time plugin configuration in website/docusaurus.config.ts
- [ ] T031 [US1] Create custom DocItem footer with previous/next navigation in website/src/theme/DocItem/Footer/index.tsx

**Checkpoint**: User Story 1 complete - educational content is browsable and readable

---

## Phase 4: User Story 2 - Ask Questions via AI Chatbot (Priority: P2)

**Goal**: Learners can ask questions and receive RAG-powered answers from textbook content

**Independent Test**: Open chatbot, ask "What is a ROS 2 node?", verify response is accurate and cites relevant chapters

### Implementation for User Story 2

#### Backend RAG Infrastructure

- [X] T032 [P] [US2] Create Qdrant client wrapper in backend/app/services/qdrant_client.py
- [X] T033 [P] [US2] Create OpenAI embedding service in backend/app/services/embedding_service.py using text-embedding-3-small
- [X] T034 [US2] Create RAG service in backend/app/services/rag_service.py with semantic search and context retrieval
- [ ] T035 [US2] Create chapter indexing script in backend/scripts/index_chapters.py to chunk MDX files and upload to Qdrant

#### Backend Chat API

- [X] T036 [P] [US2] Create ChatSession Pydantic schema in backend/app/schemas/chat.py per contracts/chat.yaml
- [X] T037 [P] [US2] Create ChatMessage Pydantic schema in backend/app/schemas/chat.py per contracts/chat.yaml
- [X] T038 [P] [US2] Create ChatSession SQLAlchemy model in backend/app/models/chat.py per data-model.md
- [X] T039 [P] [US2] Create ChatMessage SQLAlchemy model in backend/app/models/chat.py per data-model.md
- [X] T040 [US2] Create chat service in backend/app/services/chat_service.py with session management and message handling
- [X] T041 [US2] Create chat router in backend/app/routers/chat.py with POST /chat/sessions, GET /chat/sessions/{id}, POST /chat/sessions/{id}/messages endpoints
- [X] T042 [US2] Create quick question endpoint POST /chat/ask in backend/app/routers/chat.py for stateless queries

#### Frontend Chat Widget

- [X] T043 [P] [US2] Create ChatWidget component in website/src/components/ChatWidget/index.tsx
- [X] T044 [P] [US2] Create ChatWidget styles in website/src/components/ChatWidget/styles.module.css
- [X] T045 [US2] Create useChat hook in website/src/hooks/useChat.ts for chat state management and API calls
- [X] T046 [US2] Integrate ChatWidget into Docusaurus layout in website/src/theme/Root.tsx

**Checkpoint**: User Story 2 complete - AI chatbot answers questions with source citations

---

## Phase 5: User Story 3 - Create Account and Set Learning Profile (Priority: P3)

**Goal**: Learners can create accounts, set learning profiles with coding level and hardware info

**Independent Test**: Complete signup, answer profile questions, logout, login, verify profile data persists

### Implementation for User Story 3

#### Backend Authentication

- [ ] T047 [P] [US3] Create User Pydantic schema in backend/app/schemas/user.py per contracts/auth.yaml
- [ ] T048 [P] [US3] Create Session Pydantic schema in backend/app/schemas/user.py per contracts/auth.yaml
- [ ] T049 [US3] Create BetterAuth integration service in backend/app/services/auth_service.py
- [ ] T050 [US3] Create auth router in backend/app/routers/auth.py with POST /auth/signup, POST /auth/signin, POST /auth/signout, GET /auth/session endpoints

#### Backend Profile Management

- [ ] T051 [P] [US3] Create UserProfile Pydantic schema in backend/app/schemas/profile.py per contracts/profile.yaml
- [ ] T052 [P] [US3] Create UserProfile SQLAlchemy model in backend/app/models/profile.py per data-model.md
- [ ] T053 [US3] Create profile service in backend/app/services/profile_service.py with CRUD operations
- [ ] T054 [US3] Create profile router in backend/app/routers/profile.py with GET /profile, POST /profile, PUT /profile endpoints

#### Frontend Authentication & Profile

- [ ] T055 [P] [US3] Create useAuth hook in website/src/hooks/useAuth.ts for authentication state management
- [ ] T056 [P] [US3] Create AuthContext provider in website/src/context/AuthContext.tsx
- [ ] T057 [US3] Create SignupForm component in website/src/components/SignupForm/index.tsx
- [ ] T058 [US3] Create LoginForm component in website/src/components/LoginForm/index.tsx
- [ ] T059 [US3] Create ProfileForm component in website/src/components/ProfileForm/index.tsx with coding_level, has_nvidia_gpu, has_robot, robot_platform, primary_interest fields
- [ ] T060 [US3] Create profile page in website/src/pages/profile.tsx

**Checkpoint**: User Story 3 complete - users can signup, login, and manage profiles

---

## Phase 6: User Story 4 - View Personalized Content (Priority: P4)

**Goal**: Content adapts based on user profile (coding level, hardware availability)

**Independent Test**: Login as beginner without GPU, navigate to Module 2, verify Gazebo content shown prominently while Isaac Sim marked as optional

### Implementation for User Story 4

#### Backend Personalization

- [ ] T061 [P] [US4] Create PersonalizationRules Pydantic schema in backend/app/schemas/personalization.py per contracts/profile.yaml
- [ ] T062 [US4] Create personalization service in backend/app/services/personalization_service.py with rule evaluation logic
- [ ] T063 [US4] Add GET /profile/personalization endpoint to backend/app/routers/profile.py

#### Frontend Personalization

- [ ] T064 [P] [US4] Create usePersonalization hook in website/src/hooks/usePersonalization.ts
- [ ] T065 [P] [US4] Create PersonalizeButton component in website/src/components/PersonalizeButton/index.tsx
- [ ] T066 [US4] Create ConditionalContent component in website/src/components/ConditionalContent/index.tsx for MDX content filtering
- [ ] T067 [US4] Swizzle DocItem component in website/src/theme/DocItem/index.tsx to inject personalization logic
- [ ] T068 [US4] Add personalization CSS classes (.beginner-explanation, .isaac-sim-content, .gazebo-content) in website/src/css/personalization.css
- [ ] T069 [US4] Update sample chapters to include personalization markers in website/docs/module-2-simulation/intro.mdx

**Checkpoint**: User Story 4 complete - content adapts to user profile

---

## Phase 7: User Story 5 - Translate Content to Urdu (Priority: P5)

**Goal**: Learners can translate chapter content to Urdu while preserving technical terms

**Independent Test**: Click translate button on any chapter, verify Urdu text appears with terms like "ROS 2" preserved in brackets

### Implementation for User Story 5

#### Backend Translation

- [ ] T070 [P] [US5] Create Translation SQLAlchemy model in backend/app/models/translation.py per data-model.md
- [ ] T071 [P] [US5] Create TranslateRequest/TranslateResponse Pydantic schemas in backend/app/schemas/translation.py per contracts/translation.yaml
- [ ] T072 [US5] Create translation service in backend/app/services/translation_service.py with Claude API integration and caching
- [ ] T073 [US5] Create translate router in backend/app/routers/translate.py with POST /translate, GET /translate/status, GET/DELETE /translate/cache/{path} endpoints

#### Frontend Translation

- [ ] T074 [P] [US5] Create TranslateButton component in website/src/components/TranslateButton/index.tsx
- [ ] T075 [P] [US5] Create TranslateButton styles in website/src/components/TranslateButton/styles.module.css
- [ ] T076 [US5] Create useTranslation hook in website/src/hooks/useTranslation.ts
- [ ] T077 [US5] Integrate TranslateButton into DocItem header in website/src/theme/DocItem/Header/index.tsx
- [ ] T078 [US5] Create TranslatedContent component in website/src/components/TranslatedContent/index.tsx for displaying Urdu content

**Checkpoint**: User Story 5 complete - content can be translated to Urdu

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T079 [P] Create .env.example documentation with setup instructions in README.md
- [ ] T080 [P] Add API health check endpoint GET /health in backend/app/main.py
- [ ] T081 Code review and cleanup across all routers in backend/app/routers/
- [ ] T082 [P] Add loading states to all frontend components
- [ ] T083 [P] Add error boundary component in website/src/components/ErrorBoundary/index.tsx
- [ ] T084 Performance optimization: Add response caching headers in backend
- [ ] T085 Security hardening: Input validation and rate limiting in backend/app/middleware/
- [ ] T086 Run quickstart.md validation to verify developer setup works end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

| User Story | Depends On | Can Start After |
|------------|------------|-----------------|
| US1 (Browse Content) | Foundational only | Phase 2 complete |
| US2 (AI Chatbot) | Foundational only | Phase 2 complete |
| US3 (Auth/Profile) | Foundational only | Phase 2 complete |
| US4 (Personalization) | US3 (needs profiles) | Phase 5 complete |
| US5 (Translation) | US1 (needs content) | Phase 3 complete |

### Within Each User Story

- Models before services (Pydantic schemas, SQLAlchemy models)
- Services before routers (business logic before API endpoints)
- Backend before frontend integration
- Core implementation before polish

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T002, T003, T004, T005, T006 can all run in parallel
```

**Phase 2 (Foundational)**:
```
T012, T013, T014, T015, T016 can run in parallel after T009-T011
```

**User Story 1**:
```
T019, T020, T021, T022 (directory creation) can all run in parallel
T023, T024, T025, T026, T027 (chapter placeholders) can all run in parallel
```

**User Story 2**:
```
T032, T033 (Qdrant + Embedding services) can run in parallel
T036, T037, T038, T039 (schemas and models) can run in parallel
T043, T044 (ChatWidget component + styles) can run in parallel
```

**User Story 3**:
```
T047, T048 (auth schemas) can run in parallel
T051, T052 (profile schemas + model) can run in parallel
T055, T056 (auth hook + context) can run in parallel
```

---

## Parallel Example: User Story 2

```bash
# Launch all schemas/models for US2 together:
Task: "Create ChatSession Pydantic schema in backend/app/schemas/chat.py"
Task: "Create ChatMessage Pydantic schema in backend/app/schemas/chat.py"
Task: "Create ChatSession SQLAlchemy model in backend/app/models/chat.py"
Task: "Create ChatMessage SQLAlchemy model in backend/app/models/chat.py"

# Launch all frontend components for US2 together:
Task: "Create ChatWidget component in website/src/components/ChatWidget/index.tsx"
Task: "Create ChatWidget styles in website/src/components/ChatWidget/styles.module.css"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T018) - CRITICAL
3. Complete Phase 3: User Story 1 (T019-T031)
4. **STOP and VALIDATE**: Browse chapters, verify syntax highlighting works
5. Deploy/demo if ready

### Hackathon Priority Path (P1 → P2 → P3)

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Educational content browsable (MVP!)
3. Add User Story 2 → AI chatbot working
4. Add User Story 3 → Users can create accounts
5. **Hackathon Demo Ready** at this point
6. (Optional) Add US4 + US5 if time permits

### Incremental Delivery

| Checkpoint | Value Delivered |
|------------|-----------------|
| Phase 2 complete | Project foundation ready |
| US1 complete | Educational content browsable |
| US2 complete | AI learning assistant works |
| US3 complete | User accounts and profiles |
| US4 complete | Personalized content paths |
| US5 complete | Urdu translation available |

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 86 |
| **Setup Tasks** | 8 (T001-T008) |
| **Foundational Tasks** | 10 (T009-T018) |
| **US1 Tasks** | 13 (T019-T031) |
| **US2 Tasks** | 15 (T032-T046) |
| **US3 Tasks** | 14 (T047-T060) |
| **US4 Tasks** | 9 (T061-T069) |
| **US5 Tasks** | 9 (T070-T078) |
| **Polish Tasks** | 8 (T079-T086) |
| **Parallel Opportunities** | 45 tasks marked [P] |
| **MVP Scope** | US1 only (31 tasks total) |
| **Hackathon Scope** | US1-US3 (60 tasks total) |

---

## Notes

- All file paths are relative to repository root
- [P] tasks can run in parallel (different files, no dependencies)
- [Story] labels map tasks to user stories for traceability
- Tests are omitted as not explicitly requested in spec
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
