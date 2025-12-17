"""
Embeddings to Qdrant Pipeline

This module provides a complete pipeline for:
1. Extracting text content from book URLs
2. Chunking text into segments suitable for embedding
3. Generating embeddings using Cohere API
4. Storing embeddings in Qdrant vector database

Usage:
    python main.py

Environment Variables Required:
    COHERE_API_KEY: Your Cohere API key
    QDRANT_URL: Qdrant instance URL
    QDRANT_API_KEY: Qdrant API key
"""

import os
import logging
import uuid
from datetime import datetime
from typing import Optional
import time
from pathlib import Path
import re

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import cohere
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# Global clients (initialized by load_config)
_qdrant_client: Optional[QdrantClient] = None
_cohere_client: Optional[cohere.Client] = None

# Configuration defaults
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 100
DEFAULT_COLLECTION_NAME = "rag_embedding"
DEFAULT_COHERE_MODEL = "embed-english-v3.0"
DEFAULT_BASE_URL = "https://website-gm6f41dhe-haseeb-ahmeds-projects-d5ee87b2.vercel.app"


def load_config() -> dict:
    """
    Load configuration from environment variables.

    Returns:
        dict: Configuration dictionary with all settings

    Raises:
        ValueError: If required environment variables are missing
    """
    load_dotenv()

    config = {
        "cohere_api_key": os.getenv("COHERE_API_KEY"),
        "qdrant_url": os.getenv("QDRANT_URL"),
        "qdrant_api_key": os.getenv("QDRANT_API_KEY"),
        "chunk_size": int(os.getenv("CHUNK_SIZE", DEFAULT_CHUNK_SIZE)),
        "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", DEFAULT_CHUNK_OVERLAP)),
        "collection_name": os.getenv("COLLECTION_NAME", DEFAULT_COLLECTION_NAME),
        "cohere_model": os.getenv("COHERE_MODEL", DEFAULT_COHERE_MODEL),
        "base_url": os.getenv("BASE_URL", DEFAULT_BASE_URL),
    }

    # Validate required configuration
    missing = []
    if not config["cohere_api_key"]:
        missing.append("COHERE_API_KEY")
    if not config["qdrant_url"]:
        missing.append("QDRANT_URL")
    if not config["qdrant_api_key"]:
        missing.append("QDRANT_API_KEY")

    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    logger.info(f"Configuration loaded: chunk_size={config['chunk_size']}, "
                f"chunk_overlap={config['chunk_overlap']}, "
                f"collection={config['collection_name']}, "
                f"model={config['cohere_model']}")

    return config


def get_qdrant_client(config: dict) -> QdrantClient:
    """
    Initialize and return the Qdrant client.

    Args:
        config: Configuration dictionary with qdrant_url and qdrant_api_key

    Returns:
        QdrantClient: Initialized Qdrant client
    """
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(
            url=config["qdrant_url"],
            api_key=config["qdrant_api_key"]
        )
        logger.info(f"Qdrant client initialized for {config['qdrant_url']}")
    return _qdrant_client


def get_cohere_client(config: dict) -> cohere.Client:
    """
    Initialize and return the Cohere client.

    Args:
        config: Configuration dictionary with cohere_api_key

    Returns:
        cohere.Client: Initialized Cohere client
    """
    global _cohere_client
    if _cohere_client is None:
        _cohere_client = cohere.Client(api_key=config["cohere_api_key"])
        logger.info("Cohere client initialized")
    return _cohere_client


def extract_text_from_url(url: str) -> dict:
    """
    Fetch HTML from URL and extract clean text content.

    Args:
        url: The URL to fetch and extract text from

    Returns:
        dict: Contains url, title, text, and extracted_at timestamp

    Raises:
        requests.RequestException: If HTTP request fails
        ValueError: If no content could be extracted
    """
    logger.info(f"Extracting text from: {url}")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching {url}")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code} for {url}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        raise

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract title
    title = ""
    title_tag = soup.find('title')
    if title_tag:
        title = title_tag.get_text(strip=True)

    # Extract main content (Docusaurus specific selectors)
    content = ""

    # Try article first (Docusaurus docs)
    article = soup.find('article')
    if article:
        # Remove navigation, sidebar, footer elements
        for element in article.find_all(['nav', 'footer', 'aside', 'script', 'style']):
            element.decompose()
        content = article.get_text(separator=' ', strip=True)

    # Fallback to main content
    if not content:
        main = soup.find('main')
        if main:
            for element in main.find_all(['nav', 'footer', 'aside', 'script', 'style']):
                element.decompose()
            content = main.get_text(separator=' ', strip=True)

    # Final fallback to body
    if not content:
        body = soup.find('body')
        if body:
            for element in body.find_all(['nav', 'footer', 'header', 'aside', 'script', 'style']):
                element.decompose()
            content = body.get_text(separator=' ', strip=True)

    if not content:
        raise ValueError(f"No content could be extracted from {url}")

    # Clean up whitespace
    content = ' '.join(content.split())

    logger.info(f"Extracted {len(content)} characters from {url}")

    return {
        "url": url,
        "title": title,
        "text": content,
        "extracted_at": datetime.utcnow().isoformat() + "Z"
    }


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list:
    """
    Split text into overlapping chunks suitable for embedding.

    Args:
        text: The text to chunk
        chunk_size: Maximum characters per chunk (default from env or 500)
        overlap: Overlap between chunks (default from env or 100)

    Returns:
        list[dict]: List of chunk dictionaries with chunk_index, text, char_start, char_end
    """
    if chunk_size is None:
        chunk_size = int(os.getenv("CHUNK_SIZE", DEFAULT_CHUNK_SIZE))
    if overlap is None:
        overlap = int(os.getenv("CHUNK_OVERLAP", DEFAULT_CHUNK_OVERLAP))

    if not text:
        return []

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(text):
        end = start + chunk_size

        # Adjust to word boundary if not at end of text
        if end < len(text):
            # Look for last space within the chunk
            last_space = text.rfind(' ', start, end)
            if last_space > start:
                end = last_space

        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append({
                "chunk_index": chunk_index,
                "text": chunk_text,
                "char_start": start,
                "char_end": end
            })
            chunk_index += 1

        # Move start position with overlap
        start = end - overlap if end < len(text) else len(text)

        # Prevent infinite loop
        if start <= chunks[-1]["char_start"] if chunks else False:
            start = end

    logger.info(f"Created {len(chunks)} chunks (size={chunk_size}, overlap={overlap})")
    return chunks


def embed(texts: list, config: dict = None, max_retries: int = 3) -> list:
    """
    Generate embeddings for a list of texts using Cohere API.

    Args:
        texts: List of text strings to embed (max 96 per call)
        config: Configuration dictionary (uses global config if None)
        max_retries: Maximum retry attempts for rate limiting

    Returns:
        list[list[float]]: List of embedding vectors (1024 dimensions each)

    Raises:
        Exception: If embedding fails after all retries
    """
    if not texts:
        return []

    if config is None:
        config = load_config()

    client = get_cohere_client(config)
    model = config.get("cohere_model", DEFAULT_COHERE_MODEL)

    logger.info(f"Generating embeddings for {len(texts)} texts using {model}")

    # Batch if more than 96 texts
    all_embeddings = []
    batch_size = 96

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        for attempt in range(max_retries):
            try:
                response = client.embed(
                    texts=batch,
                    model=model,
                    input_type="search_document",
                    embedding_types=["float"]
                )

                # Extract float embeddings
                embeddings = response.embeddings.float
                all_embeddings.extend(embeddings)
                logger.info(f"Embedded batch {i // batch_size + 1}: {len(batch)} texts")
                break

            except Exception as e:
                if "rate" in str(e).lower() and attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Embedding failed: {e}")
                    raise

    return all_embeddings


def create_collection(config: dict, collection_name: str = None) -> bool:
    """
    Create Qdrant collection if it doesn't exist.

    Args:
        config: Configuration dictionary
        collection_name: Name for the collection (default from env or "rag_embedding")

    Returns:
        bool: True if collection exists or was created successfully
    """
    if collection_name is None:
        collection_name = config.get("collection_name", DEFAULT_COLLECTION_NAME)

    client = get_qdrant_client(config)

    try:
        if client.collection_exists(collection_name):
            logger.info(f"Collection '{collection_name}' already exists")
            return True

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1024,  # Cohere embed-english-v3.0 dimension
                distance=Distance.COSINE
            )
        )
        logger.info(f"Created collection '{collection_name}' with 1024-dim cosine vectors")
        return True

    except Exception as e:
        logger.error(f"Failed to create collection '{collection_name}': {e}")
        raise


def save_chunk_to_qdrant(
    chunks: list,
    embeddings: list,
    source_url: str,
    config: dict,
    collection_name: str = None
) -> int:
    """
    Store embeddings with metadata in Qdrant.

    Args:
        chunks: List of chunk dictionaries from chunk_text()
        embeddings: Corresponding embedding vectors
        source_url: Original document URL
        config: Configuration dictionary
        collection_name: Target collection (default from env or "rag_embedding")

    Returns:
        int: Number of points successfully stored
    """
    if collection_name is None:
        collection_name = config.get("collection_name", DEFAULT_COLLECTION_NAME)

    if len(chunks) != len(embeddings):
        raise ValueError(f"Chunk count ({len(chunks)}) doesn't match embedding count ({len(embeddings)})")

    client = get_qdrant_client(config)
    indexed_at = datetime.utcnow().isoformat() + "Z"

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
                "indexed_at": indexed_at
            }
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]

    client.upsert(
        collection_name=collection_name,
        points=points,
        wait=True
    )

    logger.info(f"Saved {len(points)} chunks to '{collection_name}' from {source_url}")
    return len(points)


def get_all_urls(base_url: str) -> list:
    """
    Get all book content URLs from the deployed website.

    Args:
        base_url: Base URL of the deployed Docusaurus site

    Returns:
        list[str]: List of documentation page URLs
    """
    # Known URLs from Docusaurus config (hardcoded for reliability)
    known_paths = [
        "/docs/intro",
        "/docs/module-1-ros/intro",
        "/docs/module-1-ros/nodes-topics",
        "/docs/module-2-simulation/intro",
        "/docs/module-3-digital-twin/intro",
        "/docs/module-4-ai-brain/intro",
    ]

    urls = [f"{base_url.rstrip('/')}{path}" for path in known_paths]

    # Try to discover more URLs from sitemap
    try:
        sitemap_url = f"{base_url.rstrip('/')}/sitemap.xml"
        response = requests.get(sitemap_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'xml')
            for loc in soup.find_all('loc'):
                url = loc.get_text()
                if '/docs/' in url and url not in urls:
                    urls.append(url)
            logger.info(f"Discovered {len(urls)} URLs from sitemap")
    except Exception as e:
        logger.warning(f"Could not fetch sitemap, using known URLs: {e}")

    logger.info(f"Total URLs to process: {len(urls)}")
    return urls


def get_local_docs(docs_dir: str) -> list:
    """
    Get all local documentation files from the docs directory.

    Args:
        docs_dir: Path to the docs directory

    Returns:
        list[dict]: List of dicts with path and relative_path for each doc file
    """
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        raise ValueError(f"Docs directory not found: {docs_dir}")

    files = []
    for ext in ['*.md', '*.mdx']:
        for file_path in docs_path.rglob(ext):
            # Skip category files
            if file_path.name.startswith('_'):
                continue
            files.append({
                'path': str(file_path),
                'relative_path': str(file_path.relative_to(docs_path))
            })

    logger.info(f"Found {len(files)} local doc files")
    return files


def extract_text_from_mdx(file_path: str) -> dict:
    """
    Extract clean text content from MDX/Markdown file.

    Args:
        file_path: Path to the MDX file

    Returns:
        dict: Contains path, title, text, and extracted_at timestamp
    """
    logger.info(f"Extracting text from: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title from frontmatter or first heading
    title = ""

    # Try frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if frontmatter_match:
        fm = frontmatter_match.group(1)
        title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', fm, re.MULTILINE)
        if title_match:
            title = title_match.group(1)
        # Remove frontmatter from content
        content = content[frontmatter_match.end():]

    # Fallback to first heading
    if not title:
        heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if heading_match:
            title = heading_match.group(1)

    # Remove MDX/JSX components
    content = re.sub(r'<[^>]+/?>', '', content)
    content = re.sub(r'import\s+.*?from\s+["\'].*?["\'];?\s*\n?', '', content)
    content = re.sub(r'export\s+.*?;?\s*\n?', '', content)

    # Remove code blocks but keep inline code
    content = re.sub(r'```[\s\S]*?```', '', content)

    # Remove markdown formatting but keep text
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)  # Links
    content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', content)  # Images
    content = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', content)  # Bold/italic
    content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)  # Headings
    content = re.sub(r'^[-*+]\s+', '', content, flags=re.MULTILINE)  # Lists
    content = re.sub(r'^\d+\.\s+', '', content, flags=re.MULTILINE)  # Numbered lists

    # Clean up whitespace
    content = ' '.join(content.split())

    if not content:
        raise ValueError(f"No content could be extracted from {file_path}")

    logger.info(f"Extracted {len(content)} characters from {file_path}")

    return {
        "url": f"file://{file_path}",
        "title": title,
        "text": content,
        "extracted_at": datetime.utcnow().isoformat() + "Z"
    }


def test_retrieval(config: dict, query: str = "What is ROS 2?", limit: int = 3) -> list:
    """
    Test retrieval by querying Qdrant with a sample question.

    Args:
        config: Configuration dictionary
        query: Search query text
        limit: Maximum number of results

    Returns:
        list: Search results with scores and payloads
    """
    logger.info(f"Testing retrieval with query: '{query}'")

    # Generate query embedding
    query_embedding = embed([query], config)[0]

    client = get_qdrant_client(config)
    collection_name = config.get("collection_name", DEFAULT_COLLECTION_NAME)

    results = client.query_points(
        collection_name=collection_name,
        query=query_embedding,
        limit=limit
    ).points

    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")

    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} (Score: {result.score:.4f}) ---")
        print(f"Source: {result.payload.get('source_url', 'N/A')}")
        print(f"Text: {result.payload.get('text', 'N/A')[:200]}...")

    print(f"\n{'='*60}\n")

    return results


def main(dry_run: bool = False, use_local: bool = False, docs_dir: str = None):
    """
    Main pipeline execution function.

    Args:
        dry_run: If True, only print files/URLs without processing
        use_local: If True, use local MDX files instead of URLs
        docs_dir: Path to local docs directory (required if use_local=True)
    """
    print("\n" + "="*60)
    print("Embeddings to Qdrant Pipeline")
    print("="*60 + "\n")

    # Load configuration
    try:
        config = load_config()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\nError: {e}")
        print("Please create a .env file with required variables.")
        print("See .env.example for template.")
        return

    # Get sources to process
    if use_local:
        if not docs_dir:
            # Default to ../website/docs relative to this script
            script_dir = Path(__file__).parent
            docs_dir = script_dir.parent / "website" / "docs"
        sources = get_local_docs(str(docs_dir))
        source_type = "local"
    else:
        base_url = config.get("base_url", DEFAULT_BASE_URL)
        sources = [{"path": url, "relative_path": url} for url in get_all_urls(base_url)]
        source_type = "url"

    if dry_run:
        print(f"\n[DRY RUN] {'Files' if use_local else 'URLs'} that would be processed:")
        for src in sources:
            print(f"  - {src['path']}")
        print(f"\nTotal: {len(sources)} {'files' if use_local else 'URLs'}")
        return

    # Create/verify collection
    collection_name = config.get("collection_name", DEFAULT_COLLECTION_NAME)
    try:
        create_collection(config, collection_name)
    except Exception as e:
        logger.error(f"Failed to initialize collection: {e}")
        return

    # Process each source
    success_count = 0
    failure_count = 0
    total_chunks = 0

    for src in sources:
        source_path = src['path']
        try:
            # Extract text based on source type
            if use_local:
                content = extract_text_from_mdx(source_path)
            else:
                content = extract_text_from_url(source_path)

            # Chunk text
            chunks = chunk_text(content["text"], config.get("chunk_size"), config.get("chunk_overlap"))

            if not chunks:
                logger.warning(f"No chunks generated for {source_path}")
                continue

            # Generate embeddings
            texts = [c["text"] for c in chunks]
            embeddings = embed(texts, config)

            # Save to Qdrant
            count = save_chunk_to_qdrant(chunks, embeddings, content["url"], config, collection_name)

            total_chunks += count
            success_count += 1
            print(f"[OK] {source_path}: {count} chunks indexed")

        except Exception as e:
            failure_count += 1
            print(f"[FAIL] {source_path}: {e}")
            logger.exception(f"Failed to process {source_path}")

    # Summary report
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"{'Files' if use_local else 'URLs'} processed: {success_count + failure_count}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {failure_count}")
    print(f"Total chunks indexed: {total_chunks}")
    print(f"Collection: {collection_name}")
    print("="*60 + "\n")

    # Test retrieval if we indexed anything
    if total_chunks > 0:
        print("Running test retrieval...")
        test_retrieval(config)


if __name__ == "__main__":
    import sys

    dry_run = "--dry-run" in sys.argv
    use_local = "--local" in sys.argv

    # Parse docs_dir argument
    docs_dir = None
    for arg in sys.argv:
        if arg.startswith("--docs-dir="):
            docs_dir = arg.split("=", 1)[1]

    main(dry_run=dry_run, use_local=use_local, docs_dir=docs_dir)
