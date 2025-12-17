"""
Qdrant client wrapper for vector storage.

Provides connection and collection management for chapter embeddings.
"""

import logging
from functools import lru_cache
from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@lru_cache
def get_qdrant_client() -> QdrantClient:
    """
    Get a cached Qdrant client instance.

    Returns:
        QdrantClient: Connected Qdrant client
    """
    logger.info(f"Connecting to Qdrant at {settings.qdrant_url}")

    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        timeout=30,
    )

    # Ensure collection exists
    ensure_collection_exists(client)

    return client


def ensure_collection_exists(client: QdrantClient) -> None:
    """
    Ensure the chapter embeddings collection exists.

    Creates collection with appropriate vector configuration if missing.
    """
    collection_name = settings.qdrant_collection

    # Determine vector size based on provider
    vector_size = 1024 if settings.ai_provider.lower() == "cohere" else 1536

    try:
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if collection_name not in collection_names:
            logger.info(f"Creating collection: {collection_name} with {vector_size}-dim vectors")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=qmodels.VectorParams(
                    size=vector_size,
                    distance=qmodels.Distance.COSINE,
                ),
            )
            logger.info(f"Collection {collection_name} created successfully")
        else:
            logger.info(f"Collection {collection_name} already exists")

    except Exception as e:
        logger.error(f"Error checking/creating collection: {e}")
        raise


def search_similar(
    query_vector: List[float],
    limit: int = 5,
    score_threshold: float = 0.7,
    filter_conditions: Optional[dict] = None,
) -> List[dict]:
    """
    Search for similar chunks in the vector store.

    Args:
        query_vector: Embedding vector for the query
        limit: Maximum number of results
        score_threshold: Minimum similarity score
        filter_conditions: Optional Qdrant filter

    Returns:
        List of matching chunks with scores and metadata
    """
    client = get_qdrant_client()

    search_filter = None
    if filter_conditions:
        search_filter = qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key=key,
                    match=qmodels.MatchValue(value=value),
                )
                for key, value in filter_conditions.items()
            ]
        )

    results = client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vector,
        limit=limit,
        score_threshold=score_threshold,
        query_filter=search_filter,
    ).points

    return [
        {
            "id": str(result.id),
            "score": result.score,
            "payload": result.payload,
        }
        for result in results
    ]


def upsert_chunks(chunks: List[dict]) -> None:
    """
    Insert or update chunks in the vector store.

    Args:
        chunks: List of chunks with 'id', 'vector', and 'payload' keys
    """
    client = get_qdrant_client()

    points = [
        qmodels.PointStruct(
            id=chunk["id"],
            vector=chunk["vector"],
            payload=chunk["payload"],
        )
        for chunk in chunks
    ]

    client.upsert(
        collection_name=settings.qdrant_collection,
        points=points,
    )

    logger.info(f"Upserted {len(chunks)} chunks to {settings.qdrant_collection}")


def delete_by_chapter(chapter_path: str) -> None:
    """
    Delete all chunks for a specific chapter.

    Args:
        chapter_path: Path of the chapter to delete
    """
    client = get_qdrant_client()

    client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=qmodels.FilterSelector(
            filter=qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="url",
                        match=qmodels.MatchText(text=chapter_path),
                    )
                ]
            )
        ),
    )

    logger.info(f"Deleted chunks for chapter: {chapter_path}")
