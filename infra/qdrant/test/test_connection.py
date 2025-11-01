
import requests
import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

headers = {
    "api-key": QDRANT_API_KEY,
}

try:
    response = requests.get(f"{QDRANT_URL}/collections", headers=headers)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
