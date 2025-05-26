from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.qdrant import  QdrantVectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import os

embed_model = SentenceTransformer("./models/all-MiniLM-L6-v2")
load_dotenv(dotenv_path=".env.local")
load_dotenv()

Qdrant_Host=os.getenv("Qdrant_Host")
Qdrant_Port=int(os.getenv("Qdrant_port"))
collectionName=os.getenv("collection_name")


client = QdrantClient(host=Qdrant_Host, port=Qdrant_Port)
vector_store = QdrantVectorStore(client=client, collection_name=collectionName)

index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    show_progress=True
)
def embed(text:str)->list[float]:
    return embed_model.encode(text).tolist()

def retrieve(query):
    query_vector=embed(query)
    search_result=client.search(
        collection_name=collectionName,
        query_vector=query_vector,
        limit=5
        
    )
    results = []
    for hit in search_result:
        results.append({
            "payload": hit.payload,
            "score": hit.score  
        })
    return results