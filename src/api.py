from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from src.agent import ask

app = FastAPI(title="Talk to Data API")

class Question(BaseModel):
    question: str

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask_endpoint(body: Question):
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is empty.")
    try:
        return ask(question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")