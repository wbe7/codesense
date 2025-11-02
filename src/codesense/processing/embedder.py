from langchain_huggingface import HuggingFaceEmbeddings
import torch

# Точное имя модели на Hugging Face Hub
MODEL_NAME = "NovaSearch/stella_en_1.5B_v5"

def get_embedding_model():
    """
    Инициализирует и возвращает модель для создания эмбеддингов.
    Автоматически выбирает GPU (cuda или mps), если он доступен.
    """
    print("Инициализация модели эмбеддингов...")
    
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"

    print(f"  Используемое устройство: {device}")

    # model_kwargs для HuggingFaceEmbeddings
    model_kwargs = {'device': device, 'trust_remote_code': True}
    
    # encode_kwargs для нормализации эмбеддингов, что улучшает качество поиска
    encode_kwargs = {'normalize_embeddings': True}

    embedding_model = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    
    print("Модель эмбеддингов успешно инициализирована.")
    return embedding_model

if __name__ == '__main__':
    # Блок для автономного тестирования этого модуля
    try:
        model = get_embedding_model()
        print("\nИнформация о модели:")
        print(model)
    except Exception as e:
        print(f"\nОшибка при инициализации модели: {e}")
