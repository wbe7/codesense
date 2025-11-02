import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

# Предполагается, что пакет codesense установлен в режиме редактирования (pip install -e .)
from codesense.utils.config import get_codebase_config
from codesense.utils.url_parser import parse_repository_info

# Определяем базовую директорию для сырых данных
RAW_DATA_DIR = os.path.join("data", "raw")

# Карта расширений файлов и соответствующих языков для сплиттера
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

def load_codebase_documents():
    """
    Загружает все файлы из локальных клонов репозиториев, определенных в codesense.yaml,
    и обогащает их метаданными.

    Returns:
        list: Список объектов Document, загруженных из всех репозиториев.
    """
    print("Загрузка и обогащение документов из кодовой базы...")
    
    repo_urls = get_codebase_config()
    all_documents = []

    for repo_url in repo_urls:
        try:
            info = parse_repository_info(repo_url)
            repo_path = os.path.join(RAW_DATA_DIR, info['id'])

            if not os.path.exists(repo_path):
                print(f"Предупреждение: Директория не найдена для репозитория {repo_url}, пропускаем: {repo_path}")
                continue

            print(f"  Загрузка файлов из: {repo_path}")
            
            loader = DirectoryLoader(
                repo_path,
                loader_cls=TextLoader,
                show_progress=True,
                use_multithreading=True,
                silent_errors=True
            )
            
            documents = loader.load()

            for doc in documents:
                doc.metadata['repo_id'] = info['id']
                doc.metadata['web_url'] = info['web_url']
                doc.metadata['file_path'] = os.path.relpath(doc.metadata['source'], repo_path)

            all_documents.extend(documents)
            print(f"  Загружено и обогащено {len(documents)} документов.")

        except Exception as e:
            print(f"Ошибка при обработке репозитория {repo_url}: {e}")

    print(f"\nВсего загружено и обогащено {len(all_documents)} документов из {len(repo_urls)} репозиториев.")
    return all_documents

def split_documents_into_chunks(documents):
    """
    Разбивает список документов на чанки с учетом синтаксиса языка.
    """
    print("\nРазбиение документов на чанки...")
    all_chunks = []
    
    for doc in documents:
        file_extension = os.path.splitext(doc.metadata.get("source", ""))[1]
        language = LANGUAGE_MAP.get(file_extension)
        
        if language:
            splitter = RecursiveCharacterTextSplitter.from_language(
                language=language, chunk_size=1000, chunk_overlap=100
            )
            chunks = splitter.split_documents([doc])
            all_chunks.extend(chunks)
        else:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=100
            )
            chunks = splitter.split_documents([doc])
            all_chunks.extend(chunks)

    print(f"Всего получено {len(all_chunks)} чанков.")
    return all_chunks


if __name__ == '__main__':
    docs = load_codebase_documents()
    
    if docs:
        chunks = split_documents_into_chunks(docs)

        print("\nПример чанков из Python-файлов (для проверки номеров строк):")
        
        # Найдем первые 2 чанка из Python файлов
        py_chunks = [c for c in chunks if c.metadata.get('file_path', '').endswith('.py')][:2]

        if py_chunks:
            for chunk in py_chunks:
                print(f"  - repo_id: {chunk.metadata.get('repo_id')}")
                print(f"    file_path: {chunk.metadata.get('file_path')}")
                print(f"    web_url: {chunk.metadata.get('web_url')}")
                print(f"    start_line: {chunk.metadata.get('loc', {}).get('lines', {}).get('from', '?')}")
                print(f"    content: '{chunk.page_content[:80].strip()}...'")
        else:
            print("  Не найдено чанков из Python-файлов для примера.")
