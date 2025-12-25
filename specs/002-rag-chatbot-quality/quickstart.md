# Quickstart: RAG Chatbot Quality Improvement

**Feature**: 002-rag-chatbot-quality
**Date**: 2025-12-25

## Overview

This feature improves RAG chatbot response quality through prompt engineering and temperature optimization. No new dependencies or infrastructure changes required.

---

## Prerequisites

- Python 3.11+
- Backend service running (`backend/`)
- Qdrant vector store with indexed content
- Cohere or OpenAI API key configured

---

## Implementation Steps

### Step 1: Update System Prompt

**File**: `backend/app/services/rag_service.py`

Replace the `_build_system_prompt()` method with enhanced grounding instructions:

```python
def _build_system_prompt(self) -> str:
    """Build the system prompt for the AI assistant."""
    return """You are an expert AI tutor for Physical AI and Humanoid Robotics.
You help students learn about ROS 2, robot simulation, digital twins, and AI integration.

IMPORTANT RULES:
1. Base your answers EXCLUSIVELY on the provided context from the textbook
2. ALWAYS cite your sources using [Source N] format (e.g., [Source 1], [Source 2])
3. If the context doesn't contain sufficient information to answer the question, respond:
   "Based on the available textbook content, I cannot fully answer this question.
   The sources I have cover [list related topics]. Would you like me to explain those instead?"
4. Never invent facts, code examples, or technical details not present in the context
5. Use examples from the context when explaining concepts

Guidelines:
- Be helpful, clear, and educational
- Format code examples with proper syntax highlighting
- Keep explanations appropriate for the student's level
- Be precise with technical terminology while remaining accessible

Remember: Your knowledge comes from the textbook context provided. Stay grounded in that content."""
```

---

### Step 2: Lower Temperature

**File**: `backend/app/services/rag_service.py`

In the `answer_question()` method, change temperature from 0.7 to 0.3:

```python
# For Cohere provider
response = self.client.chat(
    model=self.chat_model,
    message=user_prompt,
    preamble=system_prompt,
    temperature=0.3,  # Changed from 0.7
    max_tokens=1500,
)

# For OpenAI provider
response = self.client.chat.completions.create(
    model=self.chat_model,
    messages=[...],
    temperature=0.3,  # Changed from 0.7
    max_tokens=1500,
)
```

---

### Step 3: Add Retrieval Logging (Optional)

**File**: `backend/app/services/rag_service.py`

Add logging for retrieval quality metrics:

```python
# After search_similar() call
logger.info(f"Found {len(search_results)} relevant chunks")
if search_results:
    avg_score = sum(r.get('score', 0) for r in search_results) / len(search_results)
    logger.info(f"Average relevance score: {avg_score:.3f}")
```

---

## Testing

### Manual Testing

1. Start the backend server:
   ```bash
   cd backend
   python main.py
   ```

2. Test with a specific question:
   ```bash
   curl -X POST http://localhost:8000/api/chat/quick-ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What are ROS 2 nodes?"}'
   ```

3. Verify the response:
   - Contains `[Source N]` citations
   - References specific textbook content
   - Does not include generic AI knowledge

### Automated Testing

Run the existing test script:
```bash
cd backend
python test_rag.py
```

---

## Verification Checklist

- [x] System prompt updated with grounding rules
- [x] Temperature changed to 0.3
- [x] Response includes [Source N] citations
- [x] Insufficient context triggers fallback message
- [x] No generic responses for textbook questions

**Implementation completed**: 2025-12-25

---

## Rollback

If issues occur, revert to previous prompt:

1. Restore original `_build_system_prompt()` method
2. Change temperature back to 0.7

---

## Files Modified

| File | Change |
|------|--------|
| `backend/app/services/rag_service.py` | System prompt, temperature |

---

## Success Metrics

After implementation, verify:

1. Responses cite sources (look for `[Source 1]`, `[Source 2]`, etc.)
2. Questions without relevant context get fallback message
3. No hallucinated information about topics not in textbook
