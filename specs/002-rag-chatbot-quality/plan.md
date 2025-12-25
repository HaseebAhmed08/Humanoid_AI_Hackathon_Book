# Implementation Plan: RAG Chatbot Quality Improvement

**Branch**: `002-rag-chatbot-quality` | **Date**: 2025-12-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-rag-chatbot-quality/spec.md`

## Summary

Improve RAG chatbot response quality by enhancing the system prompt with explicit context-grounding rules, lowering LLM temperature for more factual responses, and adding citation requirements. This is a prompt engineering focused change with minimal code modifications.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, Cohere SDK, OpenAI SDK, qdrant-client, tenacity
**Storage**: Qdrant (vector store), Neon PostgreSQL (chat sessions)
**Testing**: Manual testing via `test_rag.py`, curl commands
**Target Platform**: Linux server (Render/Railway), Vercel serverless
**Project Type**: Web application (backend API)
**Performance Goals**: Response time <5s for RAG queries
**Constraints**: Must support both Cohere and OpenAI providers
**Scale/Scope**: Educational platform, moderate concurrent users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Multi-agent architecture (sub-agents vs skills) | ✅ PASS | This is a task for RAG Engineer role |
| Simplicity, clarity, educational value prioritized | ✅ PASS | Minimal changes, focused on prompt engineering |
| No hardcoded secrets | ✅ PASS | Uses environment variables |
| No unauthorized data access | ✅ PASS | No data access changes |
| Modular design | ✅ PASS | Changes isolated to rag_service.py |
| Smallest viable change | ✅ PASS | Only 1 file modified, ~50 lines |
| RAG Engineer responsibilities | ✅ PASS | Optimizing retrieval and response quality |
| Agent cooperation rules | ✅ PASS | No overlap with other agents |

**Constitution Check Result**: ✅ PASS - No violations

## Project Structure

### Documentation (this feature)

```text
specs/002-rag-chatbot-quality/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Research findings
├── data-model.md        # Data model documentation
├── quickstart.md        # Implementation guide
├── contracts/           # Service contracts
│   └── rag-service-interface.md
├── checklists/          # Quality checklists
│   └── requirements.md
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── services/
│   │   ├── rag_service.py      # PRIMARY FILE TO MODIFY
│   │   ├── qdrant_client.py    # No changes needed
│   │   └── embedding_service.py # No changes needed
│   └── config.py               # No changes needed
└── test_rag.py                 # Testing script
```

**Structure Decision**: Existing web application structure. Changes isolated to `backend/app/services/rag_service.py`.

## Design Decisions

### D1: Enhanced System Prompt

**Decision**: Replace generic system prompt with explicit grounding rules

**Rationale**:
- Research shows explicit "ONLY use provided context" instructions reduce hallucination
- Citation requirements ([Source N] format) improve transparency
- Explicit fallback message prevents generic responses when context is insufficient

**Implementation**: Update `_build_system_prompt()` method

### D2: Temperature Reduction

**Decision**: Lower temperature from 0.7 to 0.3

**Rationale**:
- Temperature 0.7 allows too much creativity, leading to generic responses
- Research recommends 0.1-0.3 for factual Q&A
- Temperature 0.3 balances factual grounding with natural language flow

**Implementation**: Update both Cohere and OpenAI call parameters

### D3: No Retrieval Pipeline Changes

**Decision**: Keep existing Qdrant search configuration

**Rationale**:
- Current `max_sources=5` and `score_threshold=0.3` are already optimal
- Hybrid search adds complexity without guaranteed improvement
- Focus on prompt engineering provides better ROI

**Rejected alternatives**:
- Hybrid search (vector + keyword)
- Re-ranking with cross-encoder
- Query expansion

## Implementation Phases

### Phase 1: System Prompt Enhancement
- Update `_build_system_prompt()` with grounding rules
- Add citation format requirements
- Add explicit fallback response template

### Phase 2: Temperature Optimization
- Change temperature from 0.7 to 0.3
- Update both Cohere and OpenAI provider blocks

### Phase 3: Testing & Validation
- Test with diverse questions
- Verify citation format in responses
- Test fallback behavior with out-of-scope questions

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Overly restrictive responses | Iterative prompt tuning, start with 0.3 temp |
| Breaking existing functionality | Test existing flows before and after |
| Citation format inconsistency | Include example in system prompt |

## Complexity Tracking

> No violations to justify - implementation follows smallest viable change principle

## Artifacts Generated

| Artifact | Path | Status |
|----------|------|--------|
| Research | `specs/002-rag-chatbot-quality/research.md` | ✅ Complete |
| Data Model | `specs/002-rag-chatbot-quality/data-model.md` | ✅ Complete |
| Service Contract | `specs/002-rag-chatbot-quality/contracts/rag-service-interface.md` | ✅ Complete |
| Quickstart | `specs/002-rag-chatbot-quality/quickstart.md` | ✅ Complete |
| Tasks | `specs/002-rag-chatbot-quality/tasks.md` | ⏳ Next: `/sp.tasks` |

## Next Steps

Run `/sp.tasks` to generate implementation tasks based on this plan.
