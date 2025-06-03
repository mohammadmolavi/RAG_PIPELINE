from src.retriever import retrieve
from src.generator import generate
from fastapi import FastAPI, HTTPException,Request
from typing import Optional
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException




class GenerativeRequest(BaseModel):
    question: str
    chunk_1: str
    chunk_2: Optional[str] = None
    chunk_3:Optional[str]=None


class RetrieveRequest(BaseModel):
    query: str
    heading_1: Optional[str] = None
    heading_2: Optional[str] = None

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


#general error handling
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse("error.html", {
        "request": request,
        "status_code": 500,
        "detail": "Internal Server Error"
    }, status_code=500)

# error handling : not found page
@app.exception_handler(StarletteHTTPException)
async def custom_starlette_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "status_code": 404,
            "detail":"page not found"
        }, status_code=404)
    return await custom_http_exception_handler(request, exc)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("error.html", {
        "request": request,
        "status_code": exc.status_code,
        "detail": exc.detail
    }, status_code=exc.status_code)





@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask")
def ask_question(request: RetrieveRequest):
    try:
        question = request.query
        heading_1 = request.heading_1      
        heading_2=request.heading_2
        retrieve_doc = retrieve(question,heading_1, heading_2)
        if not retrieve_doc:
            raise HTTPException(status_code=404, detail="No relevant documents found.")
        
        answer = generate(question, retrieve_doc[0]['text'],retrieve_doc[1]['text'],retrieve_doc[2]['text'])   
        return {"question": question, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/retrieve")
def retrieve_question(data:RetrieveRequest ):
    try:
        question = data.query
        heading_1 = data.heading_1
        heading_2 = data.heading_2
        retrieve_doc = retrieve(question,heading_1,heading_2)
        if not retrieve_doc:
            raise HTTPException(status_code=404, detail="No relevant documents found.")
        # print(retrieve_doc)
        return {"question": question, "documents": retrieve_doc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
def generate_answer(request: GenerativeRequest):
    try:
        
        question= request.question
        generated_doc = generate(question,request.chunk_1,request.chunk_2,request.chunk_3)
        if not generated_doc:
            raise HTTPException(status_code=404, detail="No relevant documents generated.")
        print("answer :     ",generated_doc)
        return {"question": request, "answer": generated_doc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# question ="What is the population of France ?"
# retrieve_doc=retrieve(question)
# # print(retrieve_doc[0]['text'])

# answer = generate(question, retrieve_doc[0]['text'])
# print(f"Question: {question}")
# print(f"Answer: {answer}")

