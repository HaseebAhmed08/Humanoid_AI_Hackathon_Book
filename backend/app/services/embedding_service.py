"""
Embedding service supporting both OpenAI and Cohere models.

Provides text embedding generation for RAG.
"""

import logging
from functools import lru_cache
from typing import List

from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self):
        """Initialize the embedding service based on configured provider."""
        self.provider = settings.ai_provider.lower()
        self.model = settings.embedding_model

        if self.provider == "cohere":
            import cohere
            self.client = cohere.Client(api_key=settings.cohere_api_key)
            self.dimension = 1024  # Cohere embed-english-v3.0 dimension
        else:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.dimension = 1536  # OpenAI text-embedding-3-small dimension

        logger.info(f"Embedding service initialized with {self.provider} provider")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Truncate if too long
        max_chars = 8191 * 4  # Rough estimate
        if len(text) > max_chars:
            text = text[:max_chars]
            logger.warning(f"Text truncated to {max_chars} characters")

        if self.provider == "cohere":
            response = self.client.embed(
                texts=[text],
                model=self.model,
                input_type="search_query",
                embedding_types=["float"],
            )
            return response.embeddings.float[0]
        else:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            return response.data[0].embedding

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Filter empty texts
        valid_texts = [t.strip() for t in texts if t and t.strip()]
        if not valid_texts:
            raise ValueError("No valid texts to embed")

        if self.provider == "cohere":
            # Cohere batch size limit is 96
            batch_size = 96
            all_embeddings = []

            for i in range(0, len(valid_texts), batch_size):
                batch = valid_texts[i : i + batch_size]
                response = self.client.embed(
                    texts=batch,
                    model=self.model,
                    input_type="search_document",
                    embedding_types=["float"],
                )
                all_embeddings.extend(response.embeddings.float)

            logger.info(f"Generated {len(all_embeddings)} embeddings with Cohere")
            return all_embeddings
        else:
            # OpenAI batch size limit is 100
            batch_size = 100
            all_embeddings = []

            for i in range(0, len(valid_texts), batch_size):
                batch = valid_texts[i : i + batch_size]
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                )
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

            logger.info(f"Generated {len(all_embeddings)} embeddings with OpenAI")
            return all_embeddings

    def compute_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0-1)
        """
        import math

        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = math.sqrt(sum(a * a for a in embedding1))
        norm2 = math.sqrt(sum(b * b for b in embedding2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)


@lru_cache
def get_embedding_service() -> EmbeddingService:
    """Get cached embedding service instance."""
    return EmbeddingService()
