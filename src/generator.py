from together import Together
from dotenv import load_dotenv
import os 
def build_prompt(query: str, chunk_1: str,chunk_2: str,chunk_3: str) -> str:
    prompt = f"""You are a helpful assistant. Based on the information provided belowAnswer the question **only** based on the following retrieved information, please answer the user's question accurately and thoroughly.
    If the answer is not in the context, please say 'I don’t know. Do not use any external knowledge or assumptions.

[Retrieved Information]:
f"[1]\n{chunk_1}\n\n"
f"[2]\n{chunk_2}\n\n"
f"[3]\n{chunk_3}\n\n"

[User's Question]:
"{query}"

[Please provide a clear, complete, and well-explained answer in English.]
"""
    return prompt

load_dotenv(dotenv_path=".env.local")
load_dotenv()

client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

def generate(question, chunk_1, chunk_2, chunk_3):
    prompt = build_prompt(question, chunk_1, chunk_2, chunk_3)
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.1)
    return response.choices[0].message.content