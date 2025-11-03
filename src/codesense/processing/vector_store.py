import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from langchain_qdrant import QdrantVectorStore

# Загружаем переменные окружения из .env файла
load_dotenv()


def get_qdrant_client() -> QdrantClient:
    """
    Инициализирует и возвращает клиент для подключения к Qdrant.
    Полностью настраивается через переменные окружения:
    - QDRANT_URL: хост сервера
    - QDRANT_API_KEY: ключ API
    - QDRANT_CONNECTION_METHOD: метод подключения (https, grpc), по умолчанию https
    - QDRANT_PORT: порт, по умолчанию 443 для https и 6334 для grpc
    - QDRANT_USE_TLS: использовать ли TLS (true/false), по умолчанию true
    """
    connection_method = os.getenv("QDRANT_CONNECTION_METHOD", "https").lower()
    use_tls = os.getenv("QDRANT_USE_TLS", "true").lower() == "true"
    
    client_params = {
        "host": os.getenv("QDRANT_URL"),
        "api_key": os.getenv("QDRANT_API_KEY"),
        "https": use_tls,
        "timeout": 20.0,
    }

    if connection_method == 'grpc':
        grpc_port = os.getenv("QDRANT_PORT", "6334")
        client_params["grpc_port"] = int(grpc_port)
        client_params["prefer_grpc"] = True
    else:  # По умолчанию используется HTTPS
        https_port = os.getenv("QDRANT_PORT", "443")
        client_params["port"] = int(https_port)

    return QdrantClient(**client_params)


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

if __name__ == '__main__':
    print("--- Запуск теста для vector_store.py ---")

    # Создаем мок-объект для модели эмбеддингов,
    # чтобы не импортировать тяжелые зависимости.
    class MockEmbedding:
        def embed_query(self, text: str) -> list[float]:
            # Наша модель Qwen/Qwen3-Embedding-0.6B имеет размерность 1024
            return [0.0] * 1024

    test_client = get_qdrant_client()
    print("Клиент Qdrant успешно создан.")

    create_collection_if_not_exists(
        client=test_client,
        collection_name="codesense-test",
        embedding_model=MockEmbedding()
    )

    print("\n--- Тест для vector_store.py успешно завершен ---")
