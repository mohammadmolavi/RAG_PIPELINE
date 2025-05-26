from docx import Document
import re
import unicodedata
import tiktoken
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams ,SparseVector
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer,  AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

dense_model = SentenceTransformer('./models/all-MiniLM-L6-v2')
model_path = "./models/splade"
tokenizer = AutoTokenizer.from_pretrained(model_path)
splade_model = AutoModel.from_pretrained(model_path)


def extract_data(doc_path):
    doc = Document(doc_path)
    current_headings = []  
    results = []
    for para in doc.paragraphs:
        style_name = para.style.name
        if style_name.startswith('Heading 1'):
            current_headings = [para.text.strip()]
        elif style_name.startswith('Heading 2'):
            if len(current_headings) >= 1:
                if len(current_headings) == 1:
                    current_headings.append(para.text.strip())
                else:
                    current_headings[1] = para.text.strip()
            else:
                current_headings = [None, para.text.strip()]
        else:
            if para.text.strip():
                if len(current_headings)>1:
                    metadata = {
                        "heading 1":  current_headings[0],
                        "heading 2": current_headings[1]
                    }
                else:
                    metadata = {
                        "heading 1":  current_headings[0],
                        "heading 2": None
                    }
                results.append({
                    "text": para.text.strip(),
                    "metadata": metadata
                })
    return results
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

def split_paragraphs(text):
    return [para.strip() for para in text.split('\n') if para.strip()]

def preprocess_data(raw_text):
    text = normalize_text(raw_text)
    text = clean_punctuation(text)
    paragraphs = split_paragraphs(text)
    return paragraphs

# def tokenize_chunk(text, metadata, tokenizer_name="gpt2", chunk_size=150, overlap=0.2):
#     enc = tiktoken.get_encoding(tokenizer_name)
#     tokens = enc.encode(text[0])

#     step = int(chunk_size * (1 - overlap))
#     dataset = []

#     for start in range(0, len(tokens), step):
#         end = start + chunk_size
#         chunk_tokens = tokens[start:end]
#         chunk_text = enc.decode(chunk_tokens)
        
#         chunk_entry = {
#             "text": chunk_text,
#             "metadata": metadata.copy()
#         }
#         dataset.append(chunk_entry)

#         if end >= len(tokens):
#             break

#     return dataset

def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> List[str]:
    """تقسیم متن به chunk با هم‌پوشانی"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

def get_dense_vector(text: str) -> List[float]:
    return dense_model.encode(text).tolist()

# def get_sparse_vector(text: str) -> Dict[str, float]:
#     inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
#     with torch.no_grad():
#         logits = splade_model(**inputs).logits[0]
#         sparse_vec = torch.max(logits, dim=0).values
#         indices = torch.nonzero(sparse_vec > 0).squeeze().tolist()
#         if isinstance(indices, int): indices = [indices]
#         values = sparse_vec[indices].tolist()
#         tokens = tokenizer.convert_ids_to_tokens(indices)
#         return dict(zip(tokens, values))

def get_sparse_vector_dict(text, tokenizer, model, top_k=100):
    import torch
    import torch.nn.functional as F

    model.eval()
    with torch.no_grad():
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        outputs = model(**inputs)

        # SPLADE max pooling over log(1 + relu(...))
        sparse_scores = torch.max(torch.log(1 + F.relu(outputs.last_hidden_state)), dim=1).values.squeeze()
        input_ids = inputs["input_ids"].squeeze()

        # تبدیل به dict فقط برای top_k مهم‌ترین توکن‌ها
        sparse_dict = {}
        for token_id, score in zip(input_ids.tolist(), sparse_scores.tolist()):
            if token_id in sparse_dict:
                sparse_dict[token_id] = max(sparse_dict[token_id], score)
            else:
                sparse_dict[token_id] = score

        # فقط top_k بزرگ‌ترین وزن‌ها
        sorted_items = sorted(sparse_dict.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return {str(k): float(v) for k, v in sorted_items if v > 0}
    
def embed_text_chunks(text: str, chunk_size: int = 200, overlap: int = 50) -> List[Dict]:
    chunks = chunk_text(text, chunk_size, overlap)
    results = []
    for chunk in chunks:
        dense = get_dense_vector(chunk)
        sparse = get_sparse_vector_dict(chunk, tokenizer, splade_model)
        results.append({
            "text": chunk,
            "dense_vector": dense,
            "sparse_vector": sparse
        })
    return results



def upload_chunks_to_qdrant(
    dataset,  
    collection_name="Hybrid_French_population_structure",
    qdrant_url="http://localhost",
    qdrant_port=8080,
):
    client = QdrantClient(url=qdrant_url, port=qdrant_port)
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config={
        "dense": VectorParams(size=384, distance=Distance.COSINE),
        "sparse": VectorParams(size=30522, distance=Distance.DOT)  
    }
    )

    points = []
    for i, item in enumerate(dataset):
        item["metadata"]["text"] = item["text"]
        payload = item["metadata"]
        sv_dict = item["sparse_vector"]  # فرض بر این است که این dict است
        sparse_vec = SparseVector(indices=list(sv_dict.keys()), values=list(sv_dict.values()))
        points.append(PointStruct(id=i, vector=item["dense_vector"],sparse_vector=sparse_vec, payload=payload))

    client.upsert(
        collection_name=collection_name,
        points=points
    )

    print(f"{len(points)} documents uploaded to collection '{collection_name}'.")



file_path="data\dataset.docx"

sections = extract_data(file_path)

for sec in sections:
    sec['text']=preprocess_data(sec['text'])

dataset=[]
# print(sections)
for section in sections:
    embed_cunk=embed_text_chunks(section['text'][0])
    for item in embed_cunk:
        dataset.append({
            "text": item["text"],
            "dense_vector": item["dense_vector"],
            "sparse_vector": item["sparse_vector"],
            "metadata": section["metadata"]
        })

# print(dataset)
# dataset_new=[item for sublist in dataset for item in sublist]

# model =SentenceTransformer( 'sentence-transformers/all-MiniLM-L6-v2')
# model.save('./models/all-MiniLM-L6-v2')
# model =SentenceTransformer( './models/all-MiniLM-L6-v2')

upload_chunks_to_qdrant(dataset)