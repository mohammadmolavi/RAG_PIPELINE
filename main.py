from retrieval import retrieve
from generation import generate



question ="What is the population of France ?"
retrieve_doc=retrieve(question)
# print(retrieve_doc[0]['text'])

answer = generate(question, retrieve_doc[0]['text'])
print(f"Question: {question}")
print(f"Answer: {answer}")

