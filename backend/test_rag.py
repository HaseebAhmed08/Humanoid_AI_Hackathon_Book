"""Test RAG service functionality."""
import sys
sys.path.insert(0, '.')

from app.config import get_settings
from app.services.qdrant_client import get_qdrant_client, search_similar
from app.services.embedding_service import get_embedding_service
from app.services.rag_service import get_rag_service

def test_config():
    print("=== Testing Configuration ===")
    settings = get_settings()
    print(f"Provider: {settings.ai_provider}")
    print(f"Qdrant URL: {settings.qdrant_url}")
    print(f"Collection: {settings.qdrant_collection}")
    print(f"Cohere API Key: {settings.cohere_api_key[:10]}..." if settings.cohere_api_key else "No Cohere key")
    print(f"Chat Model: {settings.chat_model}")
    print(f"Embedding Model: {settings.embedding_model}")
    return settings

def test_qdrant():
    print("\n=== Testing Qdrant Connection ===")
    try:
        client = get_qdrant_client()
        collections = client.get_collections()
        print(f"Connected! Collections: {[c.name for c in collections.collections]}")

        settings = get_settings()
        collection_info = client.get_collection(settings.qdrant_collection)
        print(f"Collection '{settings.qdrant_collection}' has {collection_info.points_count} points")
        return True
    except Exception as e:
        print(f"Qdrant Error: {e}")
        return False

def test_embedding():
    print("\n=== Testing Embedding Service ===")
    try:
        embedding_service = get_embedding_service()
        test_text = "What is ROS 2?"
        embedding = embedding_service.embed_text(test_text)
        print(f"Generated embedding with {len(embedding)} dimensions")
        return True
    except Exception as e:
        print(f"Embedding Error: {e}")
        return False

def test_vector_search():
    print("\n=== Testing Vector Search ===")
    try:
        embedding_service = get_embedding_service()
        test_text = "What is ROS 2?"
        embedding = embedding_service.embed_text(test_text)

        results = search_similar(
            query_vector=embedding,
            limit=3,
            score_threshold=0.5,
        )
        print(f"Found {len(results)} results")
        for r in results:
            print(f"  - Score: {r['score']:.3f}, Payload keys: {list(r['payload'].keys())}")
        return True
    except Exception as e:
        print(f"Search Error: {e}")
        return False

def test_rag():
    print("\n=== Testing RAG Service ===")
    try:
        rag_service = get_rag_service()
        response = rag_service.answer_question("What is ROS 2?")
        print(f"Answer: {response.answer[:200]}...")
        print(f"Sources: {len(response.sources)}")
        print(f"Processing time: {response.processing_time_ms:.0f}ms")
        return True
    except Exception as e:
        print(f"RAG Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_config()
    qdrant_ok = test_qdrant()
    embedding_ok = test_embedding()
    if qdrant_ok and embedding_ok:
        search_ok = test_vector_search()
        if search_ok:
            test_rag()
    print("\n=== Done ===")
