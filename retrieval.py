from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.qdrant import  QdrantVectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer ,  util
import os
from qdrant_client.http.models import MatchValue ,Filter,FieldCondition

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

def retrieve(
        query,
        heading1=None,
        heading2=None,
        similarity_threshold: float=0.3):
    query_vector=embed(query)

    must_conditions = []
    if heading1:
        must_conditions.append(FieldCondition(key= "heading1", match=MatchValue(value=heading1)))
    if heading2:
        must_conditions.append(FieldCondition(key= "heading2", match=MatchValue(value=heading2)))
    
    query_filter=Filter(must=must_conditions) if must_conditions else None

    search_result=client.search(
        collection_name=collectionName,
        query_vector=query_vector,
        query_filter=query_filter,
        limit=3
    )
    results = []
    for hit in search_result:
        results.append({
            "payload": hit.payload,
            "score": hit.score  
        })
    return results