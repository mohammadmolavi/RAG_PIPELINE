# RAG_PIPELINE
Build an end-to-end Retrieval-Augmented Generation (RAG) pipeline over a provided dataset. Expose two FastAPI endpoints for retrieval and generation, and design each component for robustness and high-quality outputs.

---

##  Overview

This project combines cosin similarity search with generative models by:

- preprocessing the data to get better result
- Splitting documents into manageable chunks
- Generating dense vector embeddings using a local embedding model
- Retrieving the most relevant chunks using similarity search and Hybrid Search with filtering data by headings (Qdrant)
- Constructing prompts with top-k chunks
- Generating answers via an LLM 

---

## 📁 Project Structure

RAG_pipeline/  
│  
├── data/ # Raw document and test case  
├── models/ # Local models or downloaded Hugging Face models  
├── src/  
│ ├── data.py # Text splitting logic _ Storing vectors  
│ ├── generator.py # generate answer  
│ ├── model_downloader.py # downloading models and saving them in local storage  
│ ├── retriever.py # retrieval logic  
│  
├── static/  
│ ├── script.js  
│ ├── style.css  
│  
├── templates/  
│ ├── error.html   
│ ├── Index.html  
│  
├── main.py # Main entry point to run the pipeline  
├── README.md  
└── requirements.txt  

---

## 🌐 API Access

Once the server is running, visit:

- **Base URL:** [http://localhost:8000](http://localhost:8000)
- **Interactive Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative (ReDoc):** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📡 REST API Endpoints

Your RAG pipeline exposes several RESTful endpoints via FastAPI.

### 📄 1. `POST /retrieve`

**Description**:  
Retrieves the top-k most relevant chunks from the document store based on input query and filtered by two metadata ("heading_1","heading_2").

**URL**:  
`http://localhost:8000/retrieve`

**Request Body**:

```json
{
  "query": "Why are the French not considered a unified ethnic group?",
  "heading_1":"",
  "heading_2":""
}
```
Response Example:
```json
{

"question": "Why are the French not considered a unified ethnic group?",
  "documents": [
    {
      "payload": {
        "heading_1": "People of France",
        "heading_2": "Ethnic groups",
        "text": "The French are, paradoxically, strongly conscious of belonging to a single nation, but they hardly constitute a unified ethnic group by any scientific gauge. Before the official discovery of the Americas at the end of the 15th century, France, located on the western extremity of the Old World, was regarded for centuries by Europeans as being near the edge of the known world. Generations of different migrants traveling by way of the Mediterranean from the Middle East and Africa and through Europe from Central Asia and the Nordic lands settled permanently in France, forming a variegated grouping, almost like a series of geologic strata, since they were unable to migrate any farther. Perhaps the oldest reflection of these migrations is furnished by the Basque people, who live in an isolated area west of the Pyrenees in both Spain and France, who speak a language unrelated to other European languages, and whose origin remains unclear. The Celtic tribes, known to the Romans as Gauls, spread from central Europe in the period"
      },
      "score": 0.5749531
    },
    {
      "payload": {
        "heading_1": "People of France",
        "heading_2": "Religion of France",
        "text": "About three-fifths of the French people belong to the Roman Catholic Church. Only a minority, however, regularly participate in religious worship; practice is greatest among the middle classes. The northwest (Brittany-Vendée), the east (Lorraine, Vosges, Alsace, Jura, Lyonnais, and the northern Alps), the north (Flanders), the Basque Country, and the region south of the Massif Central have a higher percentage of practicing Roman Catholics than the rest of the country. Recruitment of priests has become more difficult, even though the church, historically autonomous, is very progressive and ecumenical. Reflecting the presence of immigrants from North Africa, Algeria, and Morocco, France has one of Europe's largest Muslim populations: an estimated 5,000,000 Muslims, a sizable percentage of them living in and around Marseille in southeastern France, as well as in Paris and Lyon. Protestants, who number 700,000,"
      },
      "score": 0.46990618
    },
    {
      "payload": {
        "heading_1": "People of France",
        "heading_2": "Ethnic groups",
        "text": " both Spain and France, who speak a language unrelated to other European languages, and whose origin remains unclear. The Celtic tribes, known to the Romans as Gauls, spread from central Europe in the period 500 bce-500 ce to provide France with a major component of its population, especially in the centre and west. At the fall of the Roman Empire, there was a powerful penetration of Germanic (Teutonic) peoples, especially in northern and eastern France. The incursion of the Norsemen (Vikings) brought further Germanic influence. In addition to these many migrations, France was, over the centuries, the field of numerous battles and of prolonged occupations before becoming, in the 19th and especially in the 20th century, the prime recipient of foreign immigration into Europe, adding still other mixtures to the ethnic melting pot."
      },
      "score": 0.46711084
    }
  ]
}
```


### 🧠 2. POST /generate
Description:
Generates an answer using a generative language model based on retrieved chunks and the original question.


**URL:**
`http://localhost:8000/generate`

Request Body:
```json
{
  "question": "Why are the French not considered a unified ethnic group?",
  "chunk_1": "The French are, paradoxically, strongly conscious of belonging to a single nation, but they hardly constitute a unified ethnic group by any scientific gauge. Before the official discovery of the Americas at the end of the 15th century, France, located on the western extremity of the Old World, was regarded for centuries by Europeans as being near the edge of the known world. Generations of different migrants traveling by way of the Mediterranean from the Middle East and Africa and through Europe from Central Asia and the Nordic lands settled permanently in France, forming a variegated grouping, almost like a series of geologic strata, since they were unable to migrate any farther. Perhaps the oldest reflection of these migrations is furnished by the Basque people, who live in an isolated area west of the Pyrenees in both Spain and France, who speak a language unrelated to other European languages, and whose origin remains unclear. The Celtic tribes, known to the Romans as Gauls, spread from central Europe in the period",
  "chunk_2":"About three-fifths of the French people belong to the Roman Catholic Church. Only a minority, however, regularly participate in religious worship; practice is greatest among the middle classes. The northwest (Brittany-Vendée), the east (Lorraine, Vosges, Alsace, Jura, Lyonnais, and the northern Alps), the north (Flanders), the Basque Country, and the region south of the Massif Central have a higher percentage of practicing Roman Catholics than the rest of the country. Recruitment of priests has become more difficult, even though the church, historically autonomous, is very progressive and ecumenical. Reflecting the presence of immigrants from North Africa, Algeria, and Morocco, France has one of Europe's largest Muslim populations: an estimated 5,000,000 Muslims, a sizable percentage of them living in and around Marseille in southeastern France, as well as in Paris and Lyon. Protestants, who number 700,000,",
  "chunk_3": "both Spain and France, who speak a language unrelated to other European languages, and whose origin remains unclear. The Celtic tribes, known to the Romans as Gauls, spread from central Europe in the period 500 bce-500 ce to provide France with a major component of its population, especially in the centre and west. At the fall of the Roman Empire, there was a powerful penetration of Germanic (Teutonic) peoples, especially in northern and eastern France. The incursion of the Norsemen (Vikings) brought further Germanic influence. In addition to these many migrations, France was, over the centuries, the field of numerous battles and of prolonged occupations before becoming, in the 19th and especially in the 20th century, the prime recipient of foreign immigration into Europe, adding still other mixtures to the ethnic melting pot."
}
```

Response Example:
```json
{
  "question": {
    "question": "Why are the French not considered a unified ethnic group?",
    "chunk_1": "The French are, paradoxically, strongly conscious of belonging to a single nation, but they hardly constitute a unified ethnic group by any scientific gauge. Before the official discovery of the Americas at the end of the 15th century, France, located on the western extremity of the Old World, was regarded for centuries by Europeans as being near the edge of the known world. Generations of different migrants traveling by way of the Mediterranean from the Middle East and Africa and through Europe from Central Asia and the Nordic lands settled permanently in France, forming a variegated grouping, almost like a series of geologic strata, since they were unable to migrate any farther. Perhaps the oldest reflection of these migrations is furnished by the Basque people, who live in an isolated area west of the Pyrenees in both Spain and France, who speak a language unrelated to other European languages, and whose origin remains unclear. The Celtic tribes, known to the Romans as Gauls, spread from central Europe in the period",
    "chunk_2": "About three-fifths of the French people belong to the Roman Catholic Church. Only a minority, however, regularly participate in religious worship; practice is greatest among the middle classes. The northwest (Brittany-Vendée), the east (Lorraine, Vosges, Alsace, Jura, Lyonnais, and the northern Alps), the north (Flanders), the Basque Country, and the region south of the Massif Central have a higher percentage of practicing Roman Catholics than the rest of the country. Recruitment of priests has become more difficult, even though the church, historically autonomous, is very progressive and ecumenical. Reflecting the presence of immigrants from North Africa, Algeria, and Morocco, France has one of Europe's largest Muslim populations: an estimated 5,000,000 Muslims, a sizable percentage of them living in and around Marseille in southeastern France, as well as in Paris and Lyon. Protestants, who number 700,000,",
    "chunk_3": "both Spain and France, who speak a language unrelated to other European languages, and whose origin remains unclear. The Celtic tribes, known to the Romans as Gauls, spread from central Europe in the period 500 bce-500 ce to provide France with a major component of its population, especially in the centre and west. At the fall of the Roman Empire, there was a powerful penetration of Germanic (Teutonic) peoples, especially in northern and eastern France. The incursion of the Norsemen (Vikings) brought further Germanic influence. In addition to these many migrations, France was, over the centuries, the field of numerous battles and of prolonged occupations before becoming, in the 19th and especially in the 20th century, the prime recipient of foreign immigration into Europe, adding still other mixtures to the ethnic melting pot."
  },
  "answer": "The French are not considered a unified ethnic group because of the various migrations that have taken place throughout history, resulting in a diverse and complex population. According to the retrieved information, generations of different migrants from the Middle East, Africa, Central Asia, and the Nordic lands settled permanently in France, forming a \"variegated grouping, almost like a series of geologic strata.\" This means that the French population is composed of multiple layers of different ethnic and cultural groups that have settled in the region over time.\n\nThe presence of different tribes and groups, such as the Basque people, the Celtic tribes (known as Gauls), Germanic peoples, and Norsemen (Vikings), has contributed to the diversity of the French population. Each of"
}
```

✅ You can also test everything using the interactive docs at:
👉 http://localhost:8000/docs

---

## 📤 Prompt Template

```
f"""You are a helpful assistant. Based on the information provided belowAnswer the question **only** based on the following retrieved information, please answer the user's question accurately and thoroughly.
    If the answer is not in the context, please say 'I don’t know. Do not use any external knowledge or assumptions.

[Retrieved Information]:
f"[1]\n{chunk_1}\n\n"
f"[2]\n{chunk_2}\n\n"
f"[3]\n{chunk_3}\n\n"

[User's Question]:
"{query}"

[Please provide a clear, complete, and well-explained answer in English.]
"""


```
---
## 📦 Dependencies

- fastapi==0.115.12
- together==1.5.8
- pydantic
- python-dotenv
- qdrant-client
- python-docx
- tiktoken
- sentence_transformers
- llama-index
- llama-index-vector-stores-qdrant
- langchain
- uvicorn
- python-multipart


Install them all:
``` bash
pip install -r requiremets.txt
```


---
 
 ## 📌 Configuration Parameters

| Parameter             | Type     | Default Value                             | Description                                                           |
|-----------------------|----------|-------------------------------------------|-----------------------------------------------------------------------|
| `chunk_size`          | int      | `200`                                     | Number of tokens per chunk when splitting documents.                 |
| `chunk_overlap`       | float      | `0.2`                                      | Overlap (in tokens) between chunks to maintain context.              |
| `embedding_model`     | string   | `sentence-transformers/all-MiniLM-L6-v2` | Model used for generating embeddings.                              |
| `embedding_dim`       | int      | `384`                                     | Dimension of the embedding vectors.                                  |
| `retrieval_top_k`     | int      | `3`                                       | Number of top chunks retrieved for a query.                          |
| `similarity_threshold`| float    | `0.3`                                     | Minimum cosine similarity for a chunk to be considered relevant.     |
| `llm_model`           | string   | `meta-llama/Llama-3.3-70B-Instruct-Turbo`       | Generative model used for final answer generation.                   |
| `use_qdrant`          | bool     | `True`              | Whether to use Qdrant instead of FAISS for vector search.            |
| `qdrant_host`         | string   | `localhost`                               | Host address of Qdrant server.                                       |
| `qdrant_port`         | int      | `8080`                                    | Port Qdrant is running on (REST API).                                |                               |
| `device`              | string   | `cpu`                           | Device to run embedding/generation models on.                        |

---

## ⚙️ Installation

1. Clone the repository:

```bash
git clone https://github.com/mohammadmolavi/RAG_PIPELINE.git
cd RAG_pipeline
```

2. Install dependencies
```bash
pip install -r requirements.txt
```
---
## ▶️ Running the API Server
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
Or just:
```bash
python main.py
```
---
## 🔧 Running Qdrant with Docker
We use [Qdrant](https://qdrant.tech/) as a vector database for storing and retrieving high-dimensional embeddings.

### ▶️ Step 1: Run Qdrant in Docker
Run the following command to launch Qdrant locally:
```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```
This starts the Qdrant server on:
- **REST API:** http://localhost:6333
- **gRPC API:** http://localhost:6334 

### ▶️ Step 2: Check Health
Verify Qdrant is running:
```bash
curl http://localhost:6333/health
```
should return
```bash
{"status":"ok"}
```

### ▶️ Step 3: Connect from Python
Use qdrant-client to interact with Qdrant:
```bash
pip install qdrant-client
```
Example connection:
```bash
from qdrant_client import QdrantClient
client = QdrantClient(host="localhost", port=6333)
client.get_collections()  # List available collections
```

✅ Tip: You can use Qdrant in-memory mode for development, or with persistent storage using volume mounts if needed.
```bash
docker run \
  -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```
🧠 For more advanced configurations, check the official docs: https://qdrant.tech/documentation/


---
## 👤 Author

Created by Mohammad Molavi  
📧 Contact: mohammadmolavi976@gmail.com

