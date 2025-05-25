from retrieval import retrieve
from generation import generate
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_question(request: QuestionRequest):
    try:
        question = request.question
        retrieve_doc = retrieve(question)
        if not retrieve_doc:
            raise HTTPException(status_code=404, detail="No relevant documents found.")
        
        answer = generate(question, retrieve_doc[0]['text'])
        return {"question": question, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/retrieve")
def retrieve_question(request: QuestionRequest):
    try:
        question = request.question
        retrieve_doc = retrieve(question)
        if not retrieve_doc:
            raise HTTPException(status_code=404, detail="No relevant documents found.")
        
        return {"question": question, "documents": retrieve_doc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
def generate_answer(request: QuestionRequest):
    try:
        answer = request.question
        generated_doc = generate(request)
        if not generated_doc:
            raise HTTPException(status_code=404, detail="No relevant documents generated.")
        
        return {"question": request, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# question ="What is the population of France ?"
# retrieve_doc=retrieve(question)
# # print(retrieve_doc[0]['text'])

# answer = generate(question, retrieve_doc[0]['text'])
# print(f"Question: {question}")
# print(f"Answer: {answer}")

