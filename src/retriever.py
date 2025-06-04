from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.qdrant import  QdrantVectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer 
import os
from qdrant_client.http.models import MatchValue ,Filter,FieldCondition
import re
import unicodedata


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


def normalize_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = unicodedata.normalize("NFKC", text)
    text = ''.join(c for c in text if c.isprintable())
    return text.strip()

def clean_punctuation(text):
    text = re.sub(r'[“”«»]', '"', text)
    text = re.sub(r"[’‘]", "'", text)
    text = re.sub(r"[–—]", "-", text)
    return text

def remove_noise(text):
    text = re.sub(r"http\S+|www\S+|https\S+", '', text)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'\d{5,}', '', text)
    return text



def embed(raw_text:str)->list[float]:
    text = normalize_text(raw_text)
    text = clean_punctuation(text)
    text=remove_noise(text)
    return embed_model.encode(text).tolist()

def retrieve(
        query,
        heading_1=None,
        heading_2=None,
        similarity_threshold: float=0.5):
    query_vector=embed(query)

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