from fastapi import FastAPI, HTTPException, UploadFile, File
import tempfile
import os
from pydantic import BaseModel
from main import analyze_transcript
from transcription import transcribe_audio
from clip_engine import sliding_windows, build_clips
from clip_engine import time_based_windows
from video_engine import export_clip, export_vertical_clip
from subtitle_engine import generate_srt, get_clip_segments
from video_engine import add_subtitles
from fastapi.responses import FileResponse
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from video_engine import validate_video
import subprocess
import shutil


app = FastAPI()

MAX_UPLOAD_SIZE = 500 * 1024 * 1024

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],

)
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

        transcription = transcribe_audio(temp_path)

        analysis = analyze_transcript(
            transcription["text"]
        )

        windows = time_based_windows(
            transcription["segments"],
            min_duration=10,
            max_duration=60
        )

        clips = build_clips(
            windows,
            min_duration=10,
            max_duration=60,
            top_n=5
        )

        return {
            "transcription": transcription,
            "analysis": analysis,
            "clips": clips,
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        await file.close()




@app.post("/process-video")
async def process_video(file: UploadFile = File(...)):
    temp_path = None
    output_dir = None
    if not file.filename or not file.filename.lower().endswith(".mp4"):
        await file.close()
        raise HTTPException(
            status_code=400,
            detail="Only MP4 files are accepted"
        )

    if file.content_type not in ("video/mp4", "application/octet-stream"):
        await file.close()
        raise HTTPException(
            status_code=400,
            detail="Invalid video content type"
        )


    try:
        # 1. Save uploaded video
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp4"
        ) as temp_file:
            temp_path = temp_file.name
            total_size = 0

            while chunk := await file.read(1024 * 1024):
                total_size += len(chunk)

                if total_size > MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Video exceeds the 500 MB limit"
                    )
        
                temp_file.write(chunk)


                
        if not validate_video(temp_path):
            raise HTTPException(
                status_code=400,
                detail="Invalid or corrupted video file"
            )
 
                

        # 2. Transcribe video
        transcription = transcribe_audio(temp_path)

        # 3. Generate time windows
        windows = time_based_windows(
            transcription["segments"],
            min_duration=10,
            max_duration=60
        )

        # 4. Select best clips
        clips = build_clips(
            windows,
            min_duration=10,
            max_duration=60,
            top_n=5
        )

        
        exported_clips = []

        job_id = uuid4().hex
        output_dir = Path("exports") / job_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # Export clips with subtitles
        for index, clip in enumerate(clips, start=1):

            vertical_path = str(
                output_dir / f"vertical_clip_{index}.mp4"
            )

            export_vertical_clip(
                video_path=temp_path,
                start=clip["start"],
                end=clip["end"],
                output_path=vertical_path
            )

            clip_segments = get_clip_segments(
                transcription["segments"],
                clip["start"],
                clip["end"]
            )

            subtitle_path = str(
                output_dir / f"clip_{index}.srt"
            )

            generate_srt(
                clip_segments,
                subtitle_path
            )

            final_path = str(
                output_dir / f"final_clip_{index}.mp4"
            )

            add_subtitles(
                video_path=vertical_path,
                subtitle_path=subtitle_path,
                output_path=final_path
            )

            exported_clips.append({
                **clip,
                "file": final_path,
                "download_url": (
                    f"/download/{job_id}/{Path(final_path).name}"
                )
            })

            # Clean intermediate files
            if os.path.exists(vertical_path):
                os.remove(vertical_path)

            if os.path.exists(subtitle_path):
                os.remove(subtitle_path)


        # 6. Return results
        return {
            "job_id": job_id,
            "transcription": transcription,
            "clips": exported_clips
        }
        
   
    except subprocess.CalledProcessError as error:
        if output_dir is not None:
            shutil.rmtree(output_dir, ignore_errors=True)

        print(f"FFmpeg error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Video processing failed during FFmpeg execution"
        ) from error

    except Exception as error:
        if output_dir is not None:
            shutil.rmtree(output_dir, ignore_errors=True)

        if isinstance(error, HTTPException):
            raise

        print(f"Processing error: {error}")

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during video processing"
        ) from error


    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        await file.close()


EXPORT_DIR = Path("exports").resolve()



@app.get("/download/{job_id}/{filename}")
def download_clip(job_id: str, filename: str):

    if not (
        len(job_id) == 32
        and all(c in "0123456789abcdef" for c in job_id)
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid job ID"
        )

    if filename not in {
        f"final_clip_{i}.mp4" for i in range(1, 6)
    }:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )

    file_path = EXPORT_DIR / job_id / filename

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=filename
    )

