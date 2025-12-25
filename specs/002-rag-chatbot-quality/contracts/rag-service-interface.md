# Contract: RAG Service Interface

**Feature**: 002-rag-chatbot-quality
**Date**: 2025-12-25
**Type**: Internal Service Contract

## Overview

This contract defines the expected behavior of the `RAGService` class after the quality improvements are implemented. No API changes are made - this documents the behavioral contract.

---

## Service: RAGService

### Method: `answer_question`

```python
def answer_question(
    self,
    question: str,
    chapter_context: Optional[str] = None,
    max_sources: int = 5,
) -> RAGResponse
```

**Input Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `question` | str | Yes | User's question text |
| `chapter_context` | str | No | Current chapter the user is reading |
| `max_sources` | int | No | Maximum sources to retrieve (default: 5) |

**Output**:
```python
RAGResponse(
    answer: str,           # Context-grounded answer with [Source N] citations
    sources: List[Source], # Ordered by relevance (highest first)
    processing_time_ms: float,
    tokens_used: int
)
```

---

## Behavioral Contract

### 1. Context Retrieval

**Pre-conditions**:
- Qdrant connection is healthy
- Embedding service is available
- Question is non-empty string

**Post-conditions**:
- Returns up to `max_sources` chunks from Qdrant
- All returned chunks have `score >= 0.3`
- Chunks are ordered by relevance score (descending)

**Guarantees**:
- If no chunks meet threshold, returns empty list (not error)

---

### 2. Response Generation

**Pre-conditions**:
- LLM provider (Cohere/OpenAI) is available
- System prompt is properly configured

**Post-conditions**:
- Response uses ONLY information from retrieved context
- Response includes `[Source N]` citations for factual claims
- If context is insufficient, response contains explicit acknowledgment

**Behavioral Rules**:

| Scenario | Expected Response Pattern |
|----------|---------------------------|
| Sufficient context available | Answer with inline [Source N] citations |
| Partial context available | Answer with citations + acknowledgment of gaps |
| No relevant context | Explicit message: "Based on the available textbook content..." |
| LLM error | Graceful error message (existing behavior) |

---

### 3. Citation Format

**Required Format**:
```
"Statement from textbook [Source 1]. Another claim [Source 2][Source 3]."
```

**Source Reference**:
- `[Source 1]` maps to first chunk in `sources` list
- `[Source N]` maps to Nth chunk (1-indexed)

---

### 4. Temperature and Generation Settings

| Setting | Value | Rationale |
|---------|-------|-----------|
| `temperature` | 0.3 | Low creativity, high factual grounding |
| `max_tokens` | 1500 | Sufficient for detailed explanations |
| `top_p` | (default) | Not modified |

---

## Error Handling Contract

| Error Type | Handling |
|------------|----------|
| Embedding generation failure | Raise exception (retry via tenacity) |
| Qdrant search failure | Return empty sources, log error |
| LLM generation failure | Return error message in `answer` field |

---

## Logging Contract

**Required Log Events**:
1. Question received (truncated to 50 chars)
2. Embedding generated with dimension count
3. Search results count
4. Response generation start (provider, model)
5. Response generated (character count)

**Log Level**: INFO for normal operations, ERROR for failures

---

## Testing Contract

**Unit Test Requirements**:
1. Test with sufficient context → expects citations in response
2. Test with no context → expects fallback message
3. Test with partial context → expects acknowledgment of gaps
4. Test source ordering → expects highest relevance first

**Integration Test Requirements**:
1. End-to-end RAG flow with real Qdrant
2. Verify citation format in generated responses
