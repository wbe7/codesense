import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document

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

# 3. Recreate the collection to ensure it's clean and has the correct config
if client.collection_exists(collection_name=COLLECTION_NAME):
    client.delete_collection(collection_name=COLLECTION_NAME)

embedding_size = len(embeddings.embed_query("test")) # Get the embedding size
client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=models.VectorParams(size=embedding_size, distance=models.Distance.COSINE),
)

# 4. Initialize LangChain Qdrant vector store
qdrant = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
)

# 5. Create a small dataset
documents = [
    Document(page_content="The capital of France is Paris."),
    Document(page_content="The current king of France is a controversial topic."),
    Document(page_content="Berlin is the capital of Germany."),
    Document(page_content="Qdrant is a vector search engine."),
    Document(page_content="Sentence transformers can be used to create embeddings."),
]

# 6. Add the documents to the now-empty collection
qdrant.add_documents(documents)

print(f"Successfully inserted {len(documents)} documents into collection '{COLLECTION_NAME}'.")
