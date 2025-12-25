# Research: RAG Chatbot Quality Improvement

**Feature**: 002-rag-chatbot-quality
**Date**: 2025-12-25
**Status**: Complete

## Research Questions

### 1. How to improve context retrieval quality from Qdrant?

**Decision**: Increase `top_k` from 3 to 5 and maintain 0.3 score threshold

**Rationale**:
- Current implementation already uses `max_sources=5` in `answer_question()` method
- Score threshold of 0.3 is already implemented (lowered from 0.5)
- Research indicates optimal chunk retrieval is 3-5 chunks to balance coverage without diluting focus
- Total context should stay under 2000-3000 tokens to prevent "lost in the middle" issues

**Alternatives considered**:
- Hybrid search (vector + keyword): More complex, requires Qdrant configuration changes - rejected for MVP
- Re-ranking with cross-encoder: Adds latency and complexity - consider for future iteration
- Query expansion: Could help but adds complexity - consider for future iteration

---

### 2. How to structure prompts for context-grounded responses?

**Decision**: Implement an enhanced system prompt with explicit grounding instructions

**Rationale**:
Research shows specific patterns significantly reduce hallucination:
1. Explicit "ONLY use provided context" instruction
2. Clear fallback message when context is insufficient
3. Inline citation requirements using [Source N] format
4. Step-by-step reasoning before final answer

**Recommended System Prompt Structure**:
```
You are an educational assistant that answers questions ONLY using the provided context.

RULES:
1. Base your answer EXCLUSIVELY on the retrieved context below
2. If the context does not contain sufficient information, respond:
   "Based on the available textbook content, I cannot fully answer this question."
3. Never invent facts, statistics, or claims not present in the context
4. Cite your sources using [Source N] format when making claims
5. If information is partial, acknowledge what you know and what is missing
```

**Alternatives considered**:
- Chain-of-Verification (CoVe) prompting: More token-intensive, adds latency - consider for future
- Multi-step critique and revision: Too complex for current scope

---

### 3. Optimal LLM temperature for educational RAG?

**Decision**: Lower temperature from 0.7 to 0.3

**Rationale**:
- Current implementation uses `temperature=0.7` which allows too much creativity
- Research recommends 0.1-0.3 for factual Q&A with maximum determinism
- 0.3-0.5 for educational explanations balances accuracy with engagement
- Temperature 0.3 is optimal for educational RAG that prioritizes factual grounding

**Alternatives considered**:
- Temperature 0.1: Too rigid, may produce stilted responses
- Temperature 0.5: More engaging but higher hallucination risk
- Temperature 0.7 (current): Too creative, not grounded enough

---

### 4. How to structure retrieved context in the prompt?

**Decision**: Maintain current structured format with source numbering, add relevance score visibility

**Rationale**:
- Current implementation already uses good structure: `[Source N]`, Chapter, Section, URL, Content
- Research confirms LLMs exhibit "lost in the middle" bias - most relevant at start/end
- Current code already orders by relevance score (from Qdrant)
- Adding relevance score to metadata helps with debugging and transparency

**Context Format** (current is adequate):
```
[Source 1]
Chapter: {chapter_title}
Section: {section_title}
URL: {url}
Content:
{content}
---
```

**Alternatives considered**:
- XML-style tags: More verbose, not significantly better
- JSON format: Less readable for LLM comprehension

---

### 5. How to handle insufficient context scenarios?

**Decision**: Add explicit fallback response pattern in system prompt

**Rationale**:
- Current prompt says "If the context doesn't contain relevant information, say so honestly"
- This is too vague - LLMs often still generate generic responses
- Need explicit fallback text template
- Should also suggest related topics from available context

**Fallback Pattern**:
```
If the context does not contain relevant information, respond EXACTLY:
"Based on my available sources from the textbook, I don't have specific information
about [topic]. The textbook content I have access to covers [list available related topics].
Would you like me to explain any of these instead?"
```

**Alternatives considered**:
- Confidence scoring: Requires additional model calls - consider for future
- Return empty response: Poor UX

---

## Technical Findings

### Current Implementation Analysis

**Files to modify**:
1. `backend/app/services/rag_service.py` - Main changes
   - `_build_system_prompt()`: Enhanced prompt with grounding rules
   - `_build_user_prompt()`: Already well-structured
   - `answer_question()`: Temperature setting change

2. `backend/app/services/qdrant_client.py` - No changes needed
   - Already supports `score_threshold` and `limit` parameters
   - Current implementation is adequate

**Current Settings**:
- `max_sources`: 5 (already implemented)
- `score_threshold`: 0.3 (already implemented)
- `temperature`: 0.7 (needs change to 0.3)
- `max_tokens`: 1500 (adequate)

### Recommended Changes Summary

| Component | Current | Proposed | Impact |
|-----------|---------|----------|--------|
| System Prompt | Generic guidelines | Explicit grounding rules with citation requirements | High |
| Temperature | 0.7 | 0.3 | Medium |
| Fallback Response | Vague instruction | Explicit template | High |
| Source Citations | Optional | Required with [Source N] format | Medium |
| Context Format | Good structure | Keep current, add relevance in logs | Low |

---

## Dependencies Confirmed

1. **Qdrant Client**: Current `qdrant-client` package supports all needed features
2. **Cohere/OpenAI**: Both providers support temperature parameter
3. **Existing Embeddings**: No changes needed to embedding pipeline
4. **Database Schema**: No changes needed

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Overly restrictive responses | Medium | Medium | Test with diverse questions, tune prompt iteratively |
| Increased latency | Low | Low | Temperature change doesn't affect latency significantly |
| Citation format inconsistency | Medium | Low | Add example in system prompt |
| Breaking existing functionality | Low | High | Add unit tests before changes |

---

## Research Sources

- RAG Prompt Engineering Best Practices (2025)
- LLM Grounding Techniques - Neptune.ai
- Prompt Engineering Guide - Settings
- Qdrant Documentation
- Current codebase analysis

---

## Conclusion

The primary improvements require **prompt engineering changes only** - no architectural modifications needed. The current retrieval pipeline (Qdrant search with embeddings) is adequate. Focus should be on:

1. **Enhanced system prompt** with explicit grounding rules
2. **Lower temperature** (0.7 → 0.3) for factual responses
3. **Explicit fallback template** for insufficient context
4. **Citation requirements** in responses

Estimated implementation effort: **Small** (1-2 files, ~50-100 lines of changes)
