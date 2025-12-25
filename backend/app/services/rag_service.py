"""
RAG (Retrieval-Augmented Generation) service.

Combines vector search with LLM generation for question answering.
Supports both OpenAI and Cohere as providers.
"""

import logging
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Optional

from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.services.embedding_service import get_embedding_service
from app.services.qdrant_client import search_similar

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class Source:
    """A source reference from the knowledge base."""

    chapter: str
    section: str
    url: str
    relevance_score: float
    snippet: str


@dataclass
class RAGResponse:
    """Response from the RAG service."""

    answer: str
    sources: List[Source]
    processing_time_ms: float
    tokens_used: int


class RAGService:
    """RAG service for answering questions from textbook content."""

    def __init__(self):
        """Initialize the RAG service."""
        self.embedding_service = get_embedding_service()
        self.provider = settings.ai_provider.lower()
        self.chat_model = settings.chat_model

        if self.provider == "cohere":
            import cohere
            self.client = cohere.Client(api_key=settings.cohere_api_key)
        else:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.openai_api_key)

        logger.info(f"RAG service initialized with {self.provider} provider")

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the AI assistant."""
        return """You are an expert AI tutor for Physical AI and Humanoid Robotics.
You help students learn about ROS 2, robot simulation, digital twins, and AI integration.

IMPORTANT RULES - YOU MUST FOLLOW THESE:
1. Base your answers EXCLUSIVELY on the provided context from the textbook
2. ALWAYS cite your sources using [Source N] format (e.g., [Source 1], [Source 2])
3. If the context doesn't contain sufficient information to answer the question, respond:
   "Based on the available textbook content, I cannot fully answer this question.
   The sources I have cover [list related topics from context]. Would you like me to explain those instead?"
4. Never invent facts, code examples, or technical details not present in the context
5. Use examples from the context when explaining concepts

Guidelines:
- Be helpful, clear, and educational
- Format code examples with proper syntax highlighting
- Keep explanations appropriate for the student's level
- Be precise with technical terminology while remaining accessible

Remember: Your knowledge comes from the textbook context provided. Stay grounded in that content."""

    def _build_user_prompt(
        self,
        question: str,
        context_chunks: List[dict],
        chapter_context: Optional[str] = None,
    ) -> str:
        """Build the user prompt with context."""
        context_parts = []

        for i, chunk in enumerate(context_chunks, 1):
            payload = chunk.get("payload", {})
            # Handle both old and new payload formats
            chapter_title = payload.get("chapter_title", payload.get("source_url", "Unknown"))
            section_title = payload.get("section_title", "")
            url = payload.get("url", payload.get("source_url", ""))
            content = payload.get("content", payload.get("text", ""))

            context_parts.append(
                f"[Source {i}]\n"
                f"Chapter: {chapter_title}\n"
                f"Section: {section_title}\n"
                f"URL: {url}\n"
                f"Content:\n{content}\n"
            )

        context_text = "\n---\n".join(context_parts) if context_parts else "No relevant context found."

        prompt = f"""Context from the textbook:
{context_text}

"""
        if chapter_context:
            prompt += f"The student is currently reading: {chapter_context}\n\n"

        prompt += f"Student's question: {question}\n\nPlease provide a helpful answer based on the context above."

        return prompt

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    def answer_question(
        self,
        question: str,
        chapter_context: Optional[str] = None,
        max_sources: int = 5,
    ) -> RAGResponse:
        """
        Answer a question using RAG.

        Args:
            question: The user's question
            chapter_context: Optional current chapter for context
            max_sources: Maximum number of sources to retrieve

        Returns:
            RAGResponse with answer, sources, and metadata
        """
        start_time = time.perf_counter()

        try:
            # Generate embedding for the question
            logger.info(f"Generating embedding for question: {question[:50]}...")
            question_embedding = self.embedding_service.embed_text(question)
            logger.info(f"Embedding generated with {len(question_embedding)} dimensions")
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

        try:
            # Search for relevant chunks with lower threshold to ensure results
            logger.info("Searching for relevant chunks...")
            search_results = search_similar(
                query_vector=question_embedding,
                limit=max_sources,
                score_threshold=0.3,  # Lowered from 0.5 to capture more relevant results
            )
            logger.info(f"Found {len(search_results)} relevant chunks")
            # Log retrieval quality metrics for monitoring
            if search_results:
                avg_score = sum(r.get('score', 0) for r in search_results) / len(search_results)
                logger.info(f"Average relevance score: {avg_score:.3f}")
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            search_results = []

        # Build prompts
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            question=question,
            context_chunks=search_results,
            chapter_context=chapter_context,
        )

        # Generate response based on provider
        try:
            logger.info(f"Generating response using {self.provider} ({self.chat_model})...")
            if self.provider == "cohere":
                response = self.client.chat(
                    model=self.chat_model,
                    message=user_prompt,
                    preamble=system_prompt,
                    temperature=0.3,  # Lowered from 0.7 for more factual, context-grounded responses
                    max_tokens=1500,
                )
                answer = response.text
                if not answer:
                    logger.warning("Cohere returned empty response")
                    answer = "I apologize, but I couldn't generate a response. Please try rephrasing your question."
                # Cohere doesn't provide exact token count in same way
                tokens_used = len(user_prompt.split()) + len(answer.split())
            else:
                response = self.client.chat.completions.create(
                    model=self.chat_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3,  # Lowered from 0.7 for more factual, context-grounded responses
                    max_tokens=1500,
                )
                answer = response.choices[0].message.content
                if not answer:
                    logger.warning("OpenAI returned empty response")
                    answer = "I apologize, but I couldn't generate a response. Please try rephrasing your question."
                tokens_used = response.usage.total_tokens if response.usage else 0
            logger.info(f"Response generated: {len(answer)} characters")
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            answer = f"I'm sorry, I encountered an error while processing your question. Error: {str(e)}"
            tokens_used = 0

        # Build sources list
        sources = []
        for result in search_results:
            payload = result.get("payload", {})
            # Handle both old and new payload formats
            chapter = payload.get("chapter_title", payload.get("source_url", "Unknown"))
            section = payload.get("section_title", "")
            url = payload.get("url", payload.get("source_url", ""))
            content = payload.get("content", payload.get("text", ""))

            sources.append(
                Source(
                    chapter=chapter,
                    section=section,
                    url=url,
                    relevance_score=result.get("score", 0.0),
                    snippet=content[:200] + "..." if len(content) > 200 else content,
                )
            )

        processing_time = (time.perf_counter() - start_time) * 1000

        return RAGResponse(
            answer=answer,
            sources=sources,
            processing_time_ms=processing_time,
            tokens_used=tokens_used,
        )

    def get_suggested_questions(self, chapter_path: str, limit: int = 3) -> List[str]:
        """
        Get suggested questions for a chapter.

        Args:
            chapter_path: Path to the current chapter
            limit: Number of suggestions to return

        Returns:
            List of suggested questions
        """
        # Default suggestions based on common patterns
        suggestions = [
            "What are the key concepts in this chapter?",
            "Can you explain the main example in more detail?",
            "What are common mistakes to avoid here?",
        ]

        # In production, these would be generated based on chapter content
        return suggestions[:limit]


@lru_cache
def get_rag_service() -> RAGService:
    """Get cached RAG service instance."""
    return RAGService()
