from llama_index.core import VectorStoreIndex,SimpleDirectoryReader
from llama_index.vector_stores import QdrantVectorStore 
from llama_index.embeddings.openai import OpenAIEmbedding
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os

load_dotenv()

Qdrant_Host=os.getenv("Qdrant_Host","localhost")
Qdrant_Port=int(os.getenv("Qdrant_Port","8080"))
collection_name=os.getenv("collection_name","French_population_structure")


client = QdrantClient(host=Qdrant_Host, port=Qdrant_Port)
vector_store = QdrantVectorStore(client, collection_name=collection_name)

index = VectorStoreIndex.from_documents(
    vector_store=vector_store,
    show_progress=True
)

query_engine = index.as_query_engine(similarity_top_k=3)

def retrieve(query):
    return str(query_engine.query(query))