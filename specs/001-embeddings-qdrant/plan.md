# Implementation Plan: Embeddings to Qdrant Pipeline

**Branch**: `001-embeddings-qdrant` | **Date**: 2025-12-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-embeddings-qdrant/spec.md`

## Summary

Build a single-file Python pipeline (`main.py`) that collects book URLs from the deployed Docusaurus website, extracts text content, generates embeddings using Cohere, and stores them in Qdrant for RAG retrieval. The pipeline follows a modular function design with clear separation of concerns.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- `requests` / `httpx` - HTTP client for fetching URLs
- `beautifulsoup4` - HTML parsing and text extraction
- `cohere` - Embedding generation (Cohere Python SDK)
- `qdrant-client` - Vector database operations
**Storage**: Qdrant Cloud (or local instance)
**Testing**: pytest with integration tests
**Target Platform**: Linux/Windows server (batch processing script)
**Project Type**: Single Python script (`main.py`)
**Performance Goals**: Process 50+ URLs in a single batch run
**Constraints**: Cohere API rate limits (96 texts per embed call), Qdrant payload size limits
**Scale/Scope**: ~50-100 book chapter URLs, ~1000+ text chunks

## Constitution Check

*GATE: Must pass before implementation.*

- [x] Single file design as specified by user
- [x] Modular functions for testability
- [x] Environment variables for secrets (no hardcoded API keys)
- [x] Clear logging for progress tracking
- [x] Graceful error handling

## Project Structure

### Documentation (this feature)

```text
specs/001-embeddings-qdrant/
├── spec.md              # Feature specification
├── plan.md              # This file
├── checklists/
│   └── requirements.md  # Quality checklist
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── main.py              # Single pipeline file with all functions
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
└── tests/
    └── test_main.py     # Unit and integration tests
```

**Structure Decision**: Single `main.py` file as explicitly requested by user, placed in `backend/` directory for backend integration. All pipeline functions are contained within this file.

## Pipeline Architecture

### Data Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  get_all_urls() │───►│extract_text_from │───►│   chunk_text()  │
│                 │    │     _url()       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│     main()      │◄───│save_chunk_to_   │◄───│     embed()     │
│   (orchestrate) │    │    qdrant()      │    │   (Cohere API)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              ▲
                              │
                       ┌──────────────────┐
                       │create_collection │
                       │ (rag_embedding)  │
                       └──────────────────┘
```

### Function Specifications

#### 1. `get_all_urls(base_url: str) -> list[str]`

**Purpose**: Discover all book content URLs from the deployed website.

**Implementation**:
- Fetch the sitemap or crawl navigation links
- Filter for `/docs/` URLs only (book content)
- Return deduplicated list of URLs

**Input**: Base URL of deployed site (`https://website-gm6f41dhe-haseeb-ahmeds-projects-d5ee87b2.vercel.app/`)

**Output**: List of URLs like:
```python
[
    "https://...vercel.app/docs/intro",
    "https://...vercel.app/docs/module-1-ros/intro",
    "https://...vercel.app/docs/module-1-ros/nodes-topics",
    "https://...vercel.app/docs/module-2-simulation/intro",
    "https://...vercel.app/docs/module-3-digital-twin/intro",
    "https://...vercel.app/docs/module-4-ai-brain/intro"
]
```

**Known URLs from Docusaurus config**:
- `/docs/intro` - Main introduction
- `/docs/module-1-ros/intro` - ROS 2 Foundations
- `/docs/module-1-ros/nodes-topics` - Nodes and Topics
- `/docs/module-2-simulation/intro` - Simulation
- `/docs/module-3-digital-twin/intro` - Digital Twin
- `/docs/module-4-ai-brain/intro` - AI Brain

---

#### 2. `extract_text_from_url(url: str) -> dict`

**Purpose**: Fetch HTML and extract clean text content.

**Implementation**:
- HTTP GET request to URL
- Parse HTML with BeautifulSoup
- Extract article/main content (skip nav, footer, sidebar)
- Clean whitespace and normalize text

**Input**: Single URL string

**Output**:
```python
{
    "url": "https://...vercel.app/docs/module-1-ros/intro",
    "title": "Module 1: ROS 2 Foundations",
    "text": "Clean extracted text content...",
    "extracted_at": "2025-12-17T10:30:00Z"
}
```

---

#### 3. `chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[dict]`

**Purpose**: Split text into overlapping chunks for embedding.

**Implementation**:
- Split by character count with word boundary awareness
- Maintain overlap between chunks for context continuity
- Configurable chunk size and overlap via parameters

**Input**:
- `text`: Full extracted text
- `chunk_size`: Characters per chunk (default 500)
- `overlap`: Overlap characters (default 100)

**Output**:
```python
[
    {"chunk_index": 0, "text": "First chunk of text...", "char_start": 0, "char_end": 500},
    {"chunk_index": 1, "text": "...overlap text second chunk...", "char_start": 400, "char_end": 900},
    ...
]
```

---

#### 4. `embed(texts: list[str]) -> list[list[float]]`

**Purpose**: Generate embeddings using Cohere API.

**Implementation**:
- Use Cohere Python SDK `client.embed()`
- Model: `embed-english-v3.0` (1024 dimensions)
- Input type: `search_document` for indexing
- Batch texts (max 96 per API call)
- Handle rate limiting with retry logic

**Input**: List of text strings (max 96)

**Output**: List of embedding vectors (1024 floats each)

**API Details**:
```python
from cohere import Client

client = Client(token=os.environ["COHERE_API_KEY"])
response = client.embed(
    texts=texts,
    model="embed-english-v3.0",
    input_type="search_document",
    embedding_types=["float"]
)
return response.embeddings.float
```

---

#### 5. `create_collection(collection_name: str = "rag_embedding") -> bool`

**Purpose**: Create Qdrant collection if it doesn't exist.

**Implementation**:
- Check if collection exists
- Create with proper vector configuration
- Vector size: 1024 (Cohere embed-english-v3.0)
- Distance: Cosine similarity

**Input**: Collection name (default: `rag_embedding`)

**Output**: Boolean success status

**API Details**:
```python
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

client = QdrantClient(
    url=os.environ["QDRANT_URL"],
    api_key=os.environ["QDRANT_API_KEY"]
)

if not client.collection_exists("rag_embedding"):
    client.create_collection(
        collection_name="rag_embedding",
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
    )
```

---

#### 6. `save_chunk_to_qdrant(chunks: list[dict], embeddings: list[list[float]], source_url: str, collection_name: str = "rag_embedding") -> int`

**Purpose**: Store embeddings with metadata in Qdrant.

**Implementation**:
- Create PointStruct for each chunk
- Include metadata: source URL, chunk index, original text, timestamp
- Upsert points to collection
- Return count of stored points

**Input**:
- `chunks`: List of chunk dictionaries from `chunk_text()`
- `embeddings`: Corresponding embedding vectors
- `source_url`: Original document URL
- `collection_name`: Target collection

**Output**: Number of points successfully stored

**Payload Schema**:
```python
{
    "source_url": "https://...vercel.app/docs/module-1-ros/intro",
    "chunk_index": 0,
    "text": "Original chunk text for retrieval...",
    "char_start": 0,
    "char_end": 500,
    "indexed_at": "2025-12-17T10:30:00Z"
}
```

**API Details**:
```python
from qdrant_client.models import PointStruct
import uuid

points = [
    PointStruct(
        id=str(uuid.uuid4()),
        vector=embedding,
        payload={
            "source_url": source_url,
            "chunk_index": chunk["chunk_index"],
            "text": chunk["text"],
            "char_start": chunk["char_start"],
            "char_end": chunk["char_end"],
            "indexed_at": datetime.utcnow().isoformat()
        }
    )
    for chunk, embedding in zip(chunks, embeddings)
]

client.upsert(collection_name=collection_name, points=points, wait=True)
```

---

#### 7. `main()`

**Purpose**: Orchestrate the complete pipeline execution.

**Implementation**:
1. Load environment variables
2. Initialize Cohere and Qdrant clients
3. Create/verify collection exists
4. Get all book URLs
5. For each URL:
   - Extract text
   - Chunk text
   - Generate embeddings
   - Save to Qdrant
   - Log progress
6. Print summary report

**Execution Flow**:
```python
def main():
    # Configuration
    base_url = "https://website-gm6f41dhe-haseeb-ahmeds-projects-d5ee87b2.vercel.app"
    collection_name = "rag_embedding"

    # Initialize
    create_collection(collection_name)

    # Process
    urls = get_all_urls(base_url)
    total_chunks = 0

    for url in urls:
        try:
            content = extract_text_from_url(url)
            chunks = chunk_text(content["text"])
            texts = [c["text"] for c in chunks]
            embeddings = embed(texts)
            count = save_chunk_to_qdrant(chunks, embeddings, url, collection_name)
            total_chunks += count
            print(f"✓ {url}: {count} chunks indexed")
        except Exception as e:
            print(f"✗ {url}: {e}")

    print(f"\n=== Summary ===")
    print(f"URLs processed: {len(urls)}")
    print(f"Total chunks indexed: {total_chunks}")

if __name__ == "__main__":
    main()
```

## Environment Variables

```bash
# .env.example
COHERE_API_KEY=your-cohere-api-key
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key
CHUNK_SIZE=500
CHUNK_OVERLAP=100
```

## Dependencies

```text
# requirements.txt
requests>=2.31.0
beautifulsoup4>=4.12.0
cohere>=5.0.0
qdrant-client>=1.7.0
python-dotenv>=1.0.0
```

## Testing Strategy

### Unit Tests
- `test_chunk_text()`: Verify chunking logic with various text lengths
- `test_extract_text_from_url()`: Mock HTTP responses, verify parsing

### Integration Tests
- `test_embed()`: Verify Cohere API integration (requires API key)
- `test_qdrant_operations()`: Verify collection creation and upsert
- `test_full_pipeline()`: End-to-end test with sample URL

### Test Retrieval
```python
def test_retrieval():
    """Verify embeddings are searchable after indexing."""
    query = "What is ROS 2?"
    query_embedding = embed([query])[0]

    results = client.search(
        collection_name="rag_embedding",
        query_vector=query_embedding,
        limit=3
    )

    assert len(results) > 0
    assert "text" in results[0].payload
```

## Error Handling

| Error Type | Handling Strategy |
|-----------|-------------------|
| HTTP 404/500 | Log error, skip URL, continue batch |
| Cohere rate limit | Exponential backoff retry (3 attempts) |
| Qdrant connection | Validate connectivity before batch, fail fast |
| Empty content | Log warning, skip URL |
| Encoding errors | Force UTF-8, replace invalid chars |

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Website authentication (401) | Use public sitemap or hardcode known URLs |
| Cohere API costs | Batch efficiently, monitor usage |
| Large text chunks | Truncate to model max tokens |
| Duplicate content | Use URL+chunk_index as deduplication key |

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Create `backend/` directory structure
3. Implement functions in order: `get_all_urls` → `extract_text` → `chunk_text` → `embed` → `create_collection` → `save_chunk` → `main`
4. Test with sample URLs before full batch
5. Document pipeline usage for backend integration
