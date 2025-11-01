
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "my_test_collection"

# Initialize Qdrant client
client = QdrantClient(
    host=QDRANT_URL,
    port=443,
    https=True,
    api_key=QDRANT_API_KEY,
)

# Delete the collection
if client.collection_exists(collection_name=COLLECTION_NAME):
    client.delete_collection(collection_name=COLLECTION_NAME)
    print(f"Collection '{COLLECTION_NAME}' has been deleted.")
else:
    print(f"Collection '{COLLECTION_NAME}' does not exist.")
