from retrieval import retrieve

question ="What is the population of France ?"
retrieve_doc=retrieve(question)
print(retrieve_doc)