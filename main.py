from retrieval import retrieve
from generation import generate
from fastapi import FastAPI, HTTPException,Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

class QuestionRequest(BaseModel):
    question: str
    answer: str = None

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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
        print(retrieve_doc)
        return {"question": question, "documents": retrieve_doc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
def generate_answer(request: QuestionRequest,):
    try:
        answer = request.answer
        question= request.question
        generated_doc = generate(question,answer)
        if not generated_doc:
            raise HTTPException(status_code=404, detail="No relevant documents generated.")
        print("answer :     ",generated_doc)
        return {"question": request, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# question ="What is the population of France ?"
# retrieve_doc=retrieve(question)
# # print(retrieve_doc[0]['text'])

# answer = generate(question, retrieve_doc[0]['text'])
# print(f"Question: {question}")
# print(f"Answer: {answer}")

