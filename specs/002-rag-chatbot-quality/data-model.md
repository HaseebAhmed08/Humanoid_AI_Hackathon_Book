# Data Model: RAG Chatbot Quality Improvement

**Feature**: 002-rag-chatbot-quality
**Date**: 2025-12-25

## Overview

This feature does not introduce new data models. It modifies behavior through configuration and prompt engineering. The existing data models remain unchanged.

## Existing Entities (No Changes)

### Context Chunk (stored in Qdrant)

Represents a segment of textbook content in the vector store.

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier for the chunk |
| vector | float[1024] | Cohere embedding (or 1536 for OpenAI) |
| payload.chapter_title | string | Title of the source chapter |
| payload.section_title | string | Section within the chapter |
| payload.url | string | URL path to the chapter |
| payload.content | string | The actual text content |

**No schema changes required.**

---

### Source (in-memory dataclass)

Represents a source reference returned to the user.

```python
@dataclass
class Source:
    chapter: str          # Chapter title
    section: str          # Section title
    url: str              # Chapter URL
    relevance_score: float  # Similarity score (0-1)
    snippet: str          # Content preview (max 200 chars)
```

**No changes required.**

---

### RAGResponse (in-memory dataclass)

Represents the complete response from the RAG service.

```python
@dataclass
class RAGResponse:
    answer: str               # Generated answer text
    sources: List[Source]     # List of cited sources
    processing_time_ms: float # Total processing time
    tokens_used: int          # Tokens consumed by LLM
```

**No changes required.**

---

## Configuration Changes

### RAG Service Configuration

| Parameter | Current | Proposed | Location |
|-----------|---------|----------|----------|
| `temperature` | 0.7 | 0.3 | `rag_service.py` |
| `max_sources` | 5 | 5 (no change) | `rag_service.py` |
| `score_threshold` | 0.3 | 0.3 (no change) | `rag_service.py` |
| `max_tokens` | 1500 | 1500 (no change) | `rag_service.py` |

---

## Validation Rules

### Answer Validation (soft enforcement via prompt)

- Answer MUST reference provided context
- Answer MUST use [Source N] citation format
- Answer MUST acknowledge insufficient context when applicable

### Source Validation (existing)

- Relevance score must be >= 0.3 (score_threshold)
- Maximum 5 sources per query

---

## State Transitions

Not applicable - this feature modifies stateless processing behavior.
