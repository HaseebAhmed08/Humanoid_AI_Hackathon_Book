# Embeddings to Qdrant Pipeline

A Python pipeline that extracts text from book URLs, generates embeddings using Cohere, and stores them in Qdrant for RAG (Retrieval-Augmented Generation) retrieval.

## Features

- **URL Discovery**: Automatically discovers documentation URLs from Docusaurus sitemap
- **Text Extraction**: Extracts clean text from HTML pages using BeautifulSoup
- **Smart Chunking**: Splits text into overlapping chunks with word boundary awareness
- **Embedding Generation**: Uses Cohere's embed-english-v3.0 model (1024 dimensions)
- **Vector Storage**: Stores embeddings in Qdrant with rich metadata
- **Batch Processing**: Processes multiple URLs with progress tracking and error resilience
- **Test Retrieval**: Built-in function to verify embeddings are searchable

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
COHERE_API_KEY=your-cohere-api-key
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key
```

### 3. Run the Pipeline

```bash
python main.py
```

### Dry Run Mode

To see which URLs would be processed without actually processing them:

```bash
python main.py --dry-run
```

## Configuration

All configuration is done via environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `COHERE_API_KEY` | Yes | - | Your Cohere API key |
| `QDRANT_URL` | Yes | - | Qdrant instance URL |
| `QDRANT_API_KEY` | Yes | - | Qdrant API key |
| `CHUNK_SIZE` | No | 500 | Characters per chunk |
| `CHUNK_OVERLAP` | No | 100 | Overlap between chunks |
| `COLLECTION_NAME` | No | rag_embedding | Qdrant collection name |
| `COHERE_MODEL` | No | embed-english-v3.0 | Cohere embedding model |
| `BASE_URL` | No | (Vercel URL) | Base URL for book content |

## Pipeline Functions

### `get_all_urls(base_url)`
Discovers all documentation URLs from the website sitemap.

### `extract_text_from_url(url)`
Fetches HTML and extracts clean text content from article/main elements.

### `chunk_text(text, chunk_size, overlap)`
Splits text into overlapping chunks with word boundary awareness.

### `embed(texts, config)`
Generates embeddings using Cohere API with automatic batching and rate limit handling.

### `create_collection(config, collection_name)`
Creates Qdrant collection with 1024-dimension cosine similarity vectors.

### `save_chunk_to_qdrant(chunks, embeddings, source_url, config)`
Stores embeddings with metadata (source URL, chunk index, text, timestamps).

### `test_retrieval(config, query)`
Tests retrieval by querying Qdrant with a sample question.

### `main(dry_run)`
Orchestrates the complete pipeline execution.

## Output

The pipeline produces:

1. **Progress logs** for each URL processed
2. **Summary report** with success/failure counts
3. **Test retrieval** showing sample query results

Example output:

```
============================================================
Embeddings to Qdrant Pipeline
============================================================

✓ https://.../docs/intro: 12 chunks indexed
✓ https://.../docs/module-1-ros/intro: 8 chunks indexed
✗ https://.../docs/invalid: HTTP 404

============================================================
SUMMARY
============================================================
URLs processed: 3
  Successful: 2
  Failed: 1
Total chunks indexed: 20
Collection: rag_embedding
============================================================
```

## Error Handling

- **HTTP errors**: Logged and skipped, continues with remaining URLs
- **Rate limiting**: Automatic exponential backoff retry (3 attempts)
- **Empty content**: Logged warning, URL skipped
- **Qdrant connection**: Validates connectivity before batch processing

## Metadata Schema

Each stored point in Qdrant includes:

```json
{
  "source_url": "https://example.com/docs/intro",
  "chunk_index": 0,
  "text": "Original chunk text...",
  "char_start": 0,
  "char_end": 500,
  "indexed_at": "2025-12-17T10:30:00Z"
}
```

## Integration with RAG Chatbot

To retrieve relevant chunks for a query:

```python
from main import load_config, embed, get_qdrant_client

config = load_config()
client = get_qdrant_client(config)

# Generate query embedding
query = "What is ROS 2?"
query_embedding = embed([query], config)[0]

# Search Qdrant
results = client.search(
    collection_name="rag_embedding",
    query_vector=query_embedding,
    limit=5
)

# Use results in your chatbot
for result in results:
    print(f"Score: {result.score}")
    print(f"Text: {result.payload['text']}")
```

## License

MIT License
