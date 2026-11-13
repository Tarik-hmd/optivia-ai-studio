from fastapi import FastAPI, HTTPException, UploadFile, File
import tempfile
import os
from pydantic import BaseModel
from main import analyze_transcript
from transcription import transcribe_audio

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

@app.post("/transcribe")
def transcribe(file_path: str):
    results = transcribe_audio(file_path)
    return results

@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    content = await file.read()

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(content)
    }

@app.post("/transcribe-audio")
async def transcribe_uploaded_audio(file: UploadFile = File(...)):

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3"
        ) as temp_file:

            temp_path = temp_file.name
            content = await file.read()
            temp_file.write(content)

        result = transcribe_audio(temp_path)

        return result

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        await file.close()