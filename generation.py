from together import Together
from dotenv import load_dotenv
import os 
def build_prompt(query: str, context: str) -> str:
    # context_block = "\n".join(f"- {text}" for text in retrieved_texts)
    prompt = f"""You are a helpful assistant. Based on the information provided below, please answer the user's question accurately and thoroughly but as short as you can.

[Retrieved Information]:
"{context}"

[User's Question]:
"{query}"

[Please provide a clear, complete, and well-explained answer in English and short.]
"""
    return prompt

load_dotenv(dotenv_path=".env.local")
load_dotenv()

# print(os.getenv("TOGETHER_API_KEY"))
client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

def generate(question, context):
    prompt = build_prompt(question, context)
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=256
        )
    return response.choices[0].message.content