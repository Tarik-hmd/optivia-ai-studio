from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import analyze_transcript

app = FastAPI()

class TranscriptRequest(BaseModel):
    text: str
    min_words: int = 8
    max_words: int = 25

@app.post("/analyze")
def analyze(request: TranscriptRequest):

    if request.min_words < 1:
        raise HTTPException(
            status_code=400,
            detail="min_words must be at least 1"
        )

    if request.min_words > request.max_words:
        raise HTTPException(
            status_code=400,
            detail="min_words cannot be greater than max_words"
        )
    if request.max_words < 1:
        raise HTTPException(
            status_code=400,
            detail="max_words must be at least 1"
        ) 
    results = analyze_transcript(
        request.text,
        request.min_words,
        request.max_words
    )

    return results