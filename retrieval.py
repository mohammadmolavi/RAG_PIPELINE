from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.qdrant import  QdrantVectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer ,  util
import os
from qdrant_client.http.models import MatchValue ,Filter,FieldCondition
from numpy.linalg import norm
import numpy as np

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

def normalize(vector):
    """Normalize the vector for cosine similarity"""
    vector = np.array(vector)
    if norm(vector) == 0:
        return vector.tolist()
    return (vector / norm(vector)).tolist()
def embed(text:str)->list[float]:
    return embed_model.encode(text).tolist()

def retrieve(
        query,
        heading_1=None,
        heading_2=None,
        similarity_threshold: float=0.3):
    query_vector=normalize(embed(query))

    must_conditions = []
    if heading_1:
        must_conditions.append(FieldCondition(key= "heading_1", match=MatchValue(value=heading_1)))
    if heading_2:
        must_conditions.append(FieldCondition(key= "heading_2", match=MatchValue(value=heading_2)))
    
    query_filter=Filter(must=must_conditions) if must_conditions else None




    search_result=client.search(
        collection_name=collectionName,
        query_vector=query_vector,
        query_filter=query_filter,
        limit=3,
        score_threshold =similarity_threshold
        
        
    )
    results = []
    for hit in search_result:
        results.append({
            "payload": hit.payload,
            "score": hit.score  
        })
    return results