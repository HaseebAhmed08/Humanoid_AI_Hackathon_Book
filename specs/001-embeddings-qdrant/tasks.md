# Tasks: Embeddings to Qdrant Pipeline

**Input**: Design documents from `/specs/001-embeddings-qdrant/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Not explicitly requested - minimal test tasks included for retrieval verification only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project type**: Single Python script in `backend/` directory
- All functions contained in `backend/main.py`
- Configuration in `backend/.env.example` and `backend/requirements.txt`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create `backend/` directory structure at repository root
- [x] T002 [P] Create `backend/requirements.txt` with dependencies: requests, beautifulsoup4, cohere, qdrant-client, python-dotenv
- [x] T003 [P] Create `backend/.env.example` with COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY, CHUNK_SIZE, CHUNK_OVERLAP placeholders
- [x] T004 Create `backend/main.py` with imports, docstring, and `if __name__ == "__main__"` entry point

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Implement `load_config()` function in `backend/main.py` to load environment variables using python-dotenv
- [x] T006 [P] Implement `get_qdrant_client()` helper in `backend/main.py` to initialize QdrantClient from env vars
- [x] T007 [P] Implement `get_cohere_client()` helper in `backend/main.py` to initialize Cohere Client from env vars
- [x] T008 Add logging configuration with timestamps and levels in `backend/main.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Index Book Content for RAG (Priority: P1) 🎯 MVP

**Goal**: Ingest book content from URLs, convert to embeddings, and store in Qdrant for RAG retrieval

**Independent Test**: Run pipeline with a single sample URL and verify embeddings are stored in Qdrant and retrievable via similarity search

### Implementation for User Story 1

- [x] T009 [US1] Implement `extract_text_from_url(url: str) -> dict` in `backend/main.py` - HTTP GET, BeautifulSoup parsing, extract article content, return dict with url, title, text, extracted_at
- [x] T010 [US1] Implement `chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[dict]` in `backend/main.py` - split text with overlap, return list of chunk dicts with chunk_index, text, char_start, char_end
- [x] T011 [US1] Implement `embed(texts: list[str]) -> list[list[float]]` in `backend/main.py` - call Cohere embed API with model="embed-english-v3.0", input_type="search_document", return embeddings
- [x] T012 [US1] Implement `create_collection(collection_name: str = "rag_embedding") -> bool` in `backend/main.py` - check if exists, create with VectorParams(size=1024, distance=Distance.COSINE)
- [x] T013 [US1] Implement `save_chunk_to_qdrant(chunks, embeddings, source_url, collection_name) -> int` in `backend/main.py` - create PointStruct with UUID, upsert to Qdrant, return count
- [x] T014 [US1] Add error handling with try/except in `extract_text_from_url()` for HTTP errors (404, 500, timeout)
- [x] T015 [US1] Add error handling in `embed()` for Cohere rate limiting with exponential backoff retry (3 attempts)
- [x] T016 [US1] Add logging statements in each function to track processing progress

**Checkpoint**: At this point, User Story 1 core functions should be complete and testable with a single URL

---

## Phase 4: User Story 2 - Batch Processing of Multiple URLs (Priority: P2)

**Goal**: Process multiple book URLs in a single pipeline run with progress tracking and error resilience

**Independent Test**: Provide list of 3-5 URLs and verify all are processed, failures logged, summary report generated

### Implementation for User Story 2

- [x] T017 [US2] Implement `get_all_urls(base_url: str) -> list[str]` in `backend/main.py` - fetch sitemap or hardcode known /docs/ URLs from Docusaurus config
- [x] T018 [US2] Implement `main()` orchestration function in `backend/main.py` - load config, create collection, get URLs, process each URL in loop
- [x] T019 [US2] Add progress logging in `main()` - print "✓ {url}: {count} chunks indexed" for success, "✗ {url}: {error}" for failures
- [x] T020 [US2] Add summary report at end of `main()` - total URLs processed, success/failure counts, total chunks indexed
- [x] T021 [US2] Add graceful error handling in `main()` loop - catch exceptions per URL, continue processing remaining URLs

**Checkpoint**: At this point, batch processing should work with multiple URLs, reporting progress and handling failures

---

## Phase 5: User Story 3 - Modular and Configurable Pipeline (Priority: P3)

**Goal**: Make pipeline configurable via environment variables without code changes

**Independent Test**: Change CHUNK_SIZE and COLLECTION_NAME in .env, verify pipeline uses new values

### Implementation for User Story 3

- [x] T022 [US3] Update `chunk_text()` to read CHUNK_SIZE and CHUNK_OVERLAP from environment variables with defaults
- [x] T023 [US3] Update `create_collection()` and `save_chunk_to_qdrant()` to read COLLECTION_NAME from environment variable with default "rag_embedding"
- [x] T024 [US3] Update `embed()` to read COHERE_MODEL from environment variable with default "embed-english-v3.0"
- [x] T025 [US3] Update `.env.example` to include COLLECTION_NAME and COHERE_MODEL variables
- [x] T026 [US3] Add configuration validation in `load_config()` - check required vars exist, log loaded values

**Checkpoint**: All user stories should now be independently functional with configurable parameters

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and documentation

- [x] T027 [P] Add docstrings to all functions in `backend/main.py` with Args, Returns, and Example sections
- [x] T028 [P] Create `backend/README.md` with usage instructions, environment setup, and example commands
- [x] T029 Implement `test_retrieval()` function in `backend/main.py` - query Qdrant with sample question, print results (for manual verification)
- [ ] T030 Run full pipeline end-to-end with all book URLs and verify embeddings in Qdrant
- [x] T031 Add `--dry-run` CLI flag to `main()` that prints URLs without processing (optional enhancement)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories should proceed sequentially: US1 → US2 → US3
  - US2 depends on US1 functions (extract, chunk, embed, save)
  - US3 modifies US1/US2 functions to be configurable
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 functions being complete (uses extract, chunk, embed, save in main loop)
- **User Story 3 (P3)**: Depends on US1/US2 being complete (modifies existing functions)

### Within Each User Story

- T009 → T010 → T011 → T012 → T013 (core pipeline functions in order)
- T014, T015 can run after their respective functions (T009, T011)
- T016 can run after all US1 functions

### Parallel Opportunities

**Phase 1 - Setup:**
```
T002 (requirements.txt) || T003 (.env.example)
```

**Phase 2 - Foundational:**
```
T006 (qdrant client) || T007 (cohere client)
```

**Phase 6 - Polish:**
```
T027 (docstrings) || T028 (README)
```

---

## Parallel Example: Phase 1 Setup

```bash
# Launch in parallel:
Task T002: "Create backend/requirements.txt with dependencies"
Task T003: "Create backend/.env.example with placeholders"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T008)
3. Complete Phase 3: User Story 1 (T009-T016)
4. **STOP and VALIDATE**: Test with single URL
5. Verify embedding stored in Qdrant via `test_retrieval()`

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test with single URL → MVP Ready! 🎯
3. Add User Story 2 → Test batch processing → Full Pipeline Ready
4. Add User Story 3 → Test configuration → Production Ready
5. Polish phase → Documentation complete

### Suggested MVP Scope

**MVP = Phase 1 + Phase 2 + Phase 3 (User Story 1)**

This delivers:
- Single URL extraction and embedding
- Storage in Qdrant with metadata
- Basic error handling and logging
- Manual verification via test_retrieval()

---

## Task Summary

| Phase | Tasks | Parallel Tasks |
|-------|-------|----------------|
| Phase 1: Setup | 4 | 2 |
| Phase 2: Foundational | 4 | 2 |
| Phase 3: US1 (P1) MVP | 8 | 0 |
| Phase 4: US2 (P2) | 5 | 0 |
| Phase 5: US3 (P3) | 5 | 0 |
| Phase 6: Polish | 5 | 2 |
| **Total** | **31** | **6** |

### Tasks by User Story

- **Setup/Foundation**: 8 tasks
- **User Story 1**: 8 tasks (MVP)
- **User Story 2**: 5 tasks
- **User Story 3**: 5 tasks
- **Polish**: 5 tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All code in single file `backend/main.py` as specified
- Functions must be implemented in order within US1 (pipeline dependency)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
