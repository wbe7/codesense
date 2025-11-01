import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "my_test_collection"
MODEL_NAME = "all-MiniLM-L6-v2"

# 1. Initialize Qdrant client
client = QdrantClient(
    host=QDRANT_URL,
    port=443,
    https=True,
    api_key=QDRANT_API_KEY,
)

# 2. Initialize embedding model
embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)

# 3. Initialize LangChain Qdrant vector store
qdrant = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
)

# 4. Define a search query
query_text = "Which city is the capital of Germany?"

# 5. Perform the search with score
search_result = qdrant.similarity_search_with_score(query_text, k=3)

print("Search results:")
for result, score in search_result:
    print(f"- {result.page_content} (Score: {score:.4f})")