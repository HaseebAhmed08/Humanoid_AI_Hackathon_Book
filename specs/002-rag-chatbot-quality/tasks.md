# Tasks: RAG Chatbot Quality Improvement

**Input**: Design documents from `/specs/002-rag-chatbot-quality/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Manual testing only - no automated test tasks (not explicitly requested in spec)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project type**: Web application (backend API)
- **Primary file**: `backend/app/services/rag_service.py`
- **Test file**: `backend/test_rag.py`

---

## Phase 1: Setup (Verification)

**Purpose**: Verify current state before making changes

- [x] T001 Verify backend service runs successfully by executing `cd backend && python main.py`
- [x] T002 Run existing test script to capture baseline: `cd backend && python test_rag.py`
- [x] T003 Document current response behavior by testing with question "What are ROS 2 nodes?"

---

## Phase 2: Foundational (Backup)

**Purpose**: Create backup before modifying code

- [x] T004 Create backup of `backend/app/services/rag_service.py` for rollback capability

**Checkpoint**: Baseline captured - user story implementation can now begin

---

## Phase 3: User Story 1 & 2 - Relevant Answer Retrieval & Context-Grounded Responses (Priority: P1) 🎯 MVP

**Goal**: Ensure responses are grounded in textbook content with explicit citations, avoiding generic AI responses

**Independent Test**: Ask "What is the difference between ROS 2 topics and services?" and verify response contains [Source N] citations and references specific textbook sections

**Note**: US1 and US2 are both P1 priority and addressed by the same implementation changes (enhanced system prompt)

### Implementation for User Stories 1 & 2

- [x] T005 [US1/US2] Update `_build_system_prompt()` method in `backend/app/services/rag_service.py` with enhanced grounding rules:
  - Add explicit "Base answers EXCLUSIVELY on provided context" instruction
  - Add [Source N] citation format requirement
  - Add fallback message template for insufficient context
  - Add "never invent facts" instruction
- [x] T006 [US1/US2] Update temperature setting from 0.7 to 0.3 for Cohere provider in `backend/app/services/rag_service.py` line ~179
- [x] T007 [US1/US2] Update temperature setting from 0.7 to 0.3 for OpenAI provider in `backend/app/services/rag_service.py` line ~196
- [x] T008 [US1/US2] Test with question "What are ROS 2 nodes?" and verify response contains [Source N] citations
- [x] T009 [US1/US2] Test with out-of-scope question (e.g., "What is quantum computing?") and verify fallback message appears

**Checkpoint**: Responses should now be context-grounded with citations

---

## Phase 4: User Story 3 - Improved Search Coverage (Priority: P2)

**Goal**: Ensure system retrieves 5 context chunks for comprehensive coverage

**Independent Test**: Check logs to verify 5 chunks are retrieved per query

**Note**: This is already implemented (max_sources=5 in current code). Task is verification only.

### Verification for User Story 3

- [x] T010 [US3] Verify `max_sources=5` is set in `answer_question()` method in `backend/app/services/rag_service.py` line ~127
- [x] T011 [US3] Verify `score_threshold=0.3` is set in search call in `backend/app/services/rag_service.py` line ~156
- [x] T012 [US3] Add enhanced logging for retrieval metrics: log chunk count and average relevance score after `search_similar()` call in `backend/app/services/rag_service.py`

**Checkpoint**: Retrieval coverage confirmed and logged

---

## Phase 5: User Story 4 - Source Transparency (Priority: P3)

**Goal**: Users see exactly which textbook sections answers are based on with relevance scores

**Independent Test**: Verify response metadata includes chapter, section, URL, and relevance score for each source

**Note**: This is already implemented in current code. Task is verification only.

### Verification for User Story 4

- [x] T013 [US4] Verify `Source` dataclass includes chapter, section, url, relevance_score, snippet in `backend/app/services/rag_service.py` lines 25-32
- [x] T014 [US4] Verify sources are returned ordered by relevance score (highest first) - this is default from Qdrant
- [x] T015 [US4] Test API response and confirm sources array contains all required metadata fields

**Checkpoint**: Source transparency verified

---

## Phase 6: Polish & Validation

**Purpose**: Final validation and documentation

- [x] T016 Run full test suite: `cd backend && python test_rag.py`
- [x] T017 Test with 3 diverse questions covering different textbook topics
- [x] T018 Verify no regressions in existing chat functionality
- [x] T019 Update quickstart.md verification checklist with test results in `specs/002-rag-chatbot-quality/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Stories 1 & 2 (Phase 3)**: Depends on Foundational - CORE CHANGES
- **User Story 3 (Phase 4)**: Can run after Phase 3 (verification only)
- **User Story 4 (Phase 5)**: Can run after Phase 3 (verification only)
- **Polish (Phase 6)**: Depends on all user stories being verified

### User Story Dependencies

- **User Stories 1 & 2 (P1)**: Core implementation - must complete first
- **User Story 3 (P2)**: Verification only - independent
- **User Story 4 (P3)**: Verification only - independent

### Within User Stories 1 & 2

1. T005: Update system prompt (core change)
2. T006, T007: Update temperature settings (can be done in parallel with T005)
3. T008, T009: Testing (depends on T005-T007)

### Parallel Opportunities

```text
# After T004 (backup), these can run in parallel:
Task T005: Update system prompt
Task T006: Update Cohere temperature
Task T007: Update OpenAI temperature

# After US1/US2 complete, these can run in parallel:
Task T010, T011, T012: US3 verification tasks
Task T013, T014, T015: US4 verification tasks
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004)
3. Complete Phase 3: User Stories 1 & 2 (T005-T009)
4. **STOP and VALIDATE**: Test grounded responses with citations
5. Deploy/demo if ready - this delivers 80% of the value

### Incremental Delivery

1. Setup + Foundational → Baseline captured
2. Add US1/US2 → Test citations → **Deploy (MVP!)**
3. Verify US3 → Log retrieval metrics → Deploy
4. Verify US4 → Confirm metadata → Deploy
5. Polish → Final validation → Deploy

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 19 |
| **US1/US2 Tasks** | 5 (core implementation) |
| **US3 Tasks** | 3 (verification) |
| **US4 Tasks** | 3 (verification) |
| **Setup/Polish Tasks** | 8 |
| **Files Modified** | 1 (`backend/app/services/rag_service.py`) |
| **Estimated LOC Changed** | ~50 lines |

### MVP Scope

**Minimum viable delivery**: Complete through T009 (Phase 3)
- Enhanced system prompt with grounding rules
- Lower temperature (0.3)
- Citation format [Source N] in responses
- Fallback message for insufficient context

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US3 and US4 are verification-only because current code already implements the functionality
- Core value is in US1/US2 - prompt engineering changes
- Manual testing approach per quickstart.md
- Commit after each phase for easy rollback
