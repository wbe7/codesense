import os
import logging
from langchain_core.documents import Document

# Импортируем наши модули
from codesense.utils.config import get_codebase_config
from codesense.utils.url_parser import parse_repository_info
from codesense.processing.embedder import get_embedding_model, generate_embeddings

# Импорты из LangChain
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language


RAW_DATA_DIR = os.path.join("data", "raw")

LANGUAGE_MAP = {
    ".py": Language.PYTHON,
    ".js": Language.JS,
    ".ts": Language.TS,
    ".go": Language.GO,
    ".rs": Language.RUST,
    ".java": Language.JAVA,
    ".cpp": Language.CPP,
    ".c": Language.C,
    ".html": Language.HTML,
    ".md": Language.MARKDOWN,
}

def _calculate_start_line(full_text: str, chunk_content: str) -> int:
    """Вычисляет номер начальной строки для чанка в исходном тексте."""
    start_char_index = full_text.find(chunk_content)
    if start_char_index == -1:
        return 1
    return full_text[:start_char_index].count('\n') + 1

# Подавляем логгирование предупреждений от DirectoryLoader, чтобы не засорять вывод ошибками о бинарных файлах
logging.getLogger("langchain_community.document_loaders.directory").setLevel(logging.ERROR)

def process_and_chunk_documents():
    """
    Загружает, обрабатывает и разбивает на чанки документы из всех репозиториев.
    """
    print("Загрузка, обогащение и разбиение документов...")
    
    repo_urls = get_codebase_config()
    all_chunks = []

    for repo_url in repo_urls:
        try:
            repo_info = parse_repository_info(repo_url)
            repo_path = os.path.join(RAW_DATA_DIR, repo_info['id'])

            if not os.path.exists(repo_path):
                print(f"Предупреждение: Директория не найдена: {repo_path}, пропускаем.")
                continue

            print(f"  Обработка репозитория: {repo_path}")
            
            loader = DirectoryLoader(
                repo_path,
                loader_cls=TextLoader,
                show_progress=True,
                use_multithreading=True,
                silent_errors=True
            )
            documents = loader.load()

            for doc in documents:
                file_extension = os.path.splitext(doc.metadata.get("source", ""))[1]
                language = LANGUAGE_MAP.get(file_extension)
                
                splitter = None
                if language:
                    splitter = RecursiveCharacterTextSplitter.from_language(
                        language=language, chunk_size=1000, chunk_overlap=100
                    )
                else:
                    splitter = RecursiveCharacterTextSplitter(
                        chunk_size=1000, chunk_overlap=100
                    )
                
                text_chunks = splitter.split_text(doc.page_content)

                for text_chunk in text_chunks:
                    start_line = _calculate_start_line(doc.page_content, text_chunk)
                    
                    chunk_metadata = {
                        'repo_id': repo_info['id'],
                        'web_url': repo_info['web_url'],
                        'file_path': os.path.relpath(doc.metadata['source'], repo_path),
                        'start_line': start_line
                    }
                    
                    new_chunk_doc = Document(page_content=text_chunk, metadata=chunk_metadata)
                    all_chunks.append(new_chunk_doc)

        except Exception as e:
            print(f"Ошибка при обработке репозитория {repo_url}: {e}")

    print(f"\nВсего создано {len(all_chunks)} чанков из {len(repo_urls)} репозиториев.")
    return all_chunks


if __name__ == '__main__':
    # 1. Загрузка и разбиение на чанки
    all_chunks = process_and_chunk_documents()
    
    if all_chunks:
        # 2. Берем небольшую выборку для теста
        sample_chunks = all_chunks[:100]
        print(f"\nВзято {len(sample_chunks)} чанков для тестовой генерации эмбеддингов.")

        # 3. Инициализируем модель
        embedding_model = get_embedding_model()

        # 4. Генерируем эмбеддинги для выборки
        embeddings = generate_embeddings(sample_chunks, embedding_model)

        print(f"\nТестовый прогон завершен. Получено {len(embeddings)} векторов.")
        if embeddings:
            print(f"Размерность одного вектора: {len(embeddings[0])}")
