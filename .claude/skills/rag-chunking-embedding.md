---
name: rag-chunking-embedding
description: Chunk textbook content for vector embedding and retrieval.
inputs:
  - book_text
outputs:
  - chunks
---

Split the input text into RAG-ready chunks.

Rules:
- Chunk size: 300–500 tokens
- Keep semantic meaning intact
- Add simple metadata (chapter, section)
- Do NOT paraphrase content

Return chunks in structured JSON.
