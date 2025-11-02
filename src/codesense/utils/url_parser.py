
import re

def parse_repository_info(clone_url):
    """
    Парсит любой git URL (HTTPS или SSH) и возвращает структурированную информацию.
    """
    # Регулярное выражение для извлечения host, org, и repo_name
    match = re.match(r"(?:https?://|git@)([^:/]+)[/:]([^/]+)/([^/.]+)(?:\.git)?", clone_url)
    if not match:
        raise ValueError(f"Не удалось распарсить URL: {clone_url}")

    host, org, repo_name = match.groups()

    return {
        "id": f"{host}/{org}/{repo_name}",
        "clone_url": clone_url,
        "web_url": f"https://{host}/{org}/{repo_name}"
    }
