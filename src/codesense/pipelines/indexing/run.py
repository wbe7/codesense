import argparse
from tqdm import tqdm
from codesense.processing.document_loader import process_and_chunk_documents
from codesense.processing.embedder import get_embedding_model
from codesense.processing.vector_store import (
    get_qdrant_client,
    recreate_collection,
    get_qdrant_vector_store,
)


def run(collection_name: str, batch_size: int = 64, debug: bool = False):
    """
    Выполняет полный пайплайн индексации:
    1. Загружает и разбивает на чанки документы.
    2. Инициализирует модели и клиенты.
    3. Пересоздает коллекцию в Qdrant для обеспечения чистоты данных.
    4. Итеративно генерирует эмбеддинги и загружает их в Qdrant.
    """
    print("--- Запуск пайплайна индексации ---")

    # 1. Загрузка и разбиение на чанки
    all_chunks = process_and_chunk_documents()
    if not all_chunks:
        print("Не найдено документов для индексации. Завершение работы.")
        return

    if debug:
        print("\n*** ЗАПУСК В РЕЖИМЕ ОТЛАДКИ (DEBUG) ***")
        print("Используются только первые 512 чанков.")
        all_chunks = all_chunks[:512]

    # 2. Инициализация моделей и клиентов
    embedding_model = get_embedding_model()
    qdrant_client = get_qdrant_client()

    # 3. Пересоздание коллекции
    recreate_collection(
        client=qdrant_client,
        collection_name=collection_name,
        embedding_model=embedding_model,
    )

    # 4. Получение LangChain Vector Store
    qdrant_store = get_qdrant_vector_store(
        client=qdrant_client,
        collection_name=collection_name,
        embedding_model=embedding_model,
    )

    # 5. Итеративная обработка и загрузка
    print(f"\nНачинаем обработку и загрузку в Qdrant батчами по {batch_size} чанков...")
    
    total_chunks = len(all_chunks)
    for i in tqdm(range(0, total_chunks, batch_size), desc="Загрузка в Qdrant"):
        batch = all_chunks[i:i + batch_size]
        qdrant_store.add_documents(batch)

    print(f"Обработано и загружено {total_chunks} чанков.")
    print("--- Пайплайн индексации успешно завершен ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Запуск пайплайна индексации кода.")
    parser.add_argument(
        "--collection-name",
        type=str,
        required=True,
        help="Имя коллекции в Qdrant для индексации.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Размер батча для обработки и загрузки.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Запустить в режиме отладки, используя только первые 512 чанков."
    )
    args = parser.parse_args()

    run(
        collection_name=args.collection_name, 
        batch_size=args.batch_size, 
        debug=args.debug
    )
