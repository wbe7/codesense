import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from langchain_qdrant import QdrantVectorStore

# Загружаем переменные окружения из .env файла
load_dotenv()


def get_qdrant_client() -> QdrantClient:
    """
    Инициализирует и возвращает клиент для подключения к Qdrant.
    Использует переменные окружения QDRANT_URL и QDRANT_API_KEY.
    """
    client = QdrantClient(
        host=os.getenv("QDRANT_URL"),
        port=443,
        https=True,
        api_key=os.getenv("QDRANT_API_KEY"),
        timeout=20.0,
    )
    return client


def create_collection_if_not_exists(
    client: QdrantClient,
    collection_name: str,
    embedding_model
):
    """
    Создает коллекцию в Qdrant, если она еще не существует.
    Динамически определяет размер векторов на основе используемой embedding-модели.
    """
    if not client.collection_exists(collection_name=collection_name):
        print(f"Коллекция '{collection_name}' не найдена. Создаем новую...")
        
        # Динамически определяем размер эмбеддингов
        embedding_size = len(embedding_model.embed_query("test"))
        print(f"  Размер векторов для эмбеддингов: {embedding_size}")

        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=embedding_size,
                distance=models.Distance.COSINE
            ),
        )
        print(f"Коллекция '{collection_name}' успешно создана.")
    else:
        print(f"Коллекция '{collection_name}' уже существует.")


def get_qdrant_vector_store(client: QdrantClient, collection_name: str, embedding_model) -> QdrantVectorStore:
    """
    Инициализирует и возвращает обертку QdrantVectorStore от LangChain.
    """
    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embedding_model,
    )
