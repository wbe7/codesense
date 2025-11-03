import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
import torch

# Загружаем переменные окружения из .env файла (если он есть)
load_dotenv()

# Получаем имя модели из переменной окружения или используем значение по умолчанию
MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "Qwen/Qwen3-Embedding-0.6B")

def get_embedding_model():
    """
    Инициализирует и возвращает модель для создания эмбеддингов.
    Автоматически выбирает GPU (cuda или mps), если он доступен.
    """
    print(f"Инициализация модели эмбеддингов: {MODEL_NAME}")
    
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"

    print(f"  Используемое устройство: {device}")

    model_kwargs = {'device': device, 'trust_remote_code': True}
    encode_kwargs = {'normalize_embeddings': True}

    embedding_model = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
        show_progress=True
    )
    
    print("Модель эмбеддингов успешно инициализирована.")
    return embedding_model

def generate_embeddings(chunks, embedding_model):
    """
    Генерирует эмбеддинги для списка чанков.
    """
    print(f"\nГенерация эмбеддингов для {len(chunks)} чанков...")
    
    texts = [chunk.page_content for chunk in chunks]
    
    embeddings = embedding_model.embed_documents(texts)
    
    print(f"Успешно сгенерировано {len(embeddings)} эмбеддингов.")
    return embeddings

if __name__ == '__main__':
    try:
        model = get_embedding_model()
        print("\nИнформация о модели:")
        print(model)
    except Exception as e:
        print(f"\nОшибка при инициализации модели: {e}")

