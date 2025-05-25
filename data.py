from docx import Document
import re
import unicodedata
import tiktoken
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from sentence_transformers import SentenceTransformer


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

def tokenize_chunk(text, metadata, tokenizer_name="gpt2", chunk_size=100, overlap=0.1):
    enc = tiktoken.get_encoding(tokenizer_name)
    tokens = enc.encode(text[0])

    step = int(chunk_size * (1 - overlap))
    dataset = []

    for start in range(0, len(tokens), step):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)
        
        chunk_entry = {
            "text": chunk_text,
            "metadata": metadata.copy()
        }
        dataset.append(chunk_entry)

        if end >= len(tokens):
            break

    return dataset

def upload_chunks_to_qdrant(
    dataset,  
    collection_name="French_population_structure",
    qdrant_url="http://localhost",
    qdrant_port=8080,
    embed_model=None
):
    model=embed_model
    client = QdrantClient(url=qdrant_url, port=qdrant_port)
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=model.get_sentence_embedding_dimension(),
            distance=Distance.COSINE
        )
    )

    points = []
    for i, item in enumerate(dataset):
        vector = model.encode(item["text"]).tolist()
        item["metadata"]["text"] = item["text"]
        payload = item["metadata"]
        points.append(PointStruct(id=i, vector=vector, payload=payload))

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
for section in sections:
    dataset.append(tokenize_chunk(section['text'],section['metadata']))



dataset_new=[item for sublist in dataset for item in sublist]

# model =SentenceTransformer( 'sentence-transformers/all-MiniLM-L6-v2')
# model.save('./models/all-MiniLM-L6-v2')
model =SentenceTransformer( './models/all-MiniLM-L6-v2')

upload_chunks_to_qdrant(dataset_new,embed_model=model)