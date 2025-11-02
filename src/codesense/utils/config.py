import os
import yaml
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла в корне проекта.
# Это не перезапишет уже существующие системные переменные окружения.
load_dotenv()

def get_qdrant_config() -> tuple[str, str]:
    """
    Загружает конфигурацию Qdrant из переменных окружения.

    Returns:
        tuple[str, str]: URL и API ключ для Qdrant.
    """
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    if not url or not api_key:
        raise ValueError("QDRANT_URL и QDRANT_API_KEY должны быть установлены как переменные окружения или в .env файле")
    return url, api_key

def get_codebase_config(config_path: str = "codesense.yaml") -> list[str]:
    """
    Загружает список репозиториев из главного конфигурационного файла.

    Args:
        config_path (str): Путь к файлу codesense.yaml.

    Returns:
        list[str]: Список URL репозиториев.
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        repositories = config.get('repositories')
        if not repositories or not isinstance(repositories, list):
            raise ValueError("Файл конфигурации должен содержать список 'repositories'")
        
        return repositories
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл конфигурации '{config_path}' не найден.")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Ошибка парсинга YAML в файле '{config_path}': {e}")

if __name__ == '__main__':
    # Пример использования и проверки
    try:
        qdrant_url, qdrant_api_key = get_qdrant_config()
        print(f"Qdrant URL: {qdrant_url}")
        print(f"Qdrant API Key: {'*' * len(qdrant_api_key) if qdrant_api_key else 'Not set'}")

        repos = get_codebase_config()
        print(f"Found {len(repos)} repositories in config:")
        for repo in repos:
            print(f"- {repo}")

    except (ValueError, FileNotFoundError, yaml.YAMLError) as e:
        print(f"Error: {e}")
