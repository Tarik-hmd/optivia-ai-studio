from pathlib import Path
import re
import subprocess
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from subtitle_engine import generate_srt

router = APIRouter()
ROOT = Path("exports").resolve()

class Caption(BaseModel):
    start: float = Field(ge=0, le=60)
    end: float = Field(gt=0, le=60)
    text: str = Field(max_length=1000)

class Edit(BaseModel):
    start: float = Field(ge=0, le=60)
    end: float = Field(gt=0, le=60)
    captions: list[Caption] = Field(max_length=300)
    color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    size: int = Field(ge=12, le=32)
    position: str = Field(pattern=r"^(top|middle|bottom)$")
    bold: bool = False

def source(job, index):
    if not re.fullmatch(r"[0-9a-f]{32}", job) or not 1 <= index <= 5:
        raise HTTPException(400, "Invalid clip")
    path = ROOT / job / f"vertical_clip_{index}.mp4"
    if not path.is_file():
        raise HTTPException(404, "Editable source unavailable; regenerate the project")
    return path

@router.get("/editor/{job}/{index}/source")
def preview(job: str, index: int):
    return FileResponse(source(job, index), media_type="video/mp4")

@router.post("/editor/{job}/{index}/render")
def render(job: str, index: int, edit: Edit):
    path = source(job, index)
    if edit.end - edit.start < 0.5:
        raise HTTPException(422, "Select at least 0.5 seconds")
    token = uuid4().hex
    work = path.parent
    sub = work / f"edit_{token}.srt"
    out = work / f"edit_{token}.mp4"
    try:
        duration = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)], timeout=30))
        if edit.end > duration + 0.15:
            raise HTTPException(422, "Trim exceeds source duration")
        segments = []
        for c in edit.captions:
            if c.end <= c.start:
                raise HTTPException(422, "Invalid caption timing")
            start, end = max(c.start, edit.start), min(c.end, edit.end)
            if end > start and c.text.strip():
                segments.append(dict(start=start-edit.start, end=end-edit.start, text=c.text.replace("\n", " ").replace("\r", " ")))
        cmd = ["ffmpeg", "-nostdin", "-y", "-ss", str(edit.start), "-i", path.name, "-t", str(edit.end-edit.start)]
        if segments:
            generate_srt(segments, sub)
            color = edit.color[5:7]+edit.color[3:5]+edit.color[1:3]
            align = {"top":8,"middle":5,"bottom":2}[edit.position]
            style = f"FontName=Arial,FontSize={edit.size},PrimaryColour=&H00{color},OutlineColour=&H00000000,Outline=2,Alignment={align},MarginV=45,Bold={-1 if edit.bold else 0}"
            cmd += ["-vf", f"subtitles={sub.name}:force_style='{style}'"]
        cmd += ["-c:v","libx264","-preset","veryfast","-crf","23","-pix_fmt","yuv420p","-c:a","aac","-movflags","+faststart",out.name]
        subprocess.run(cmd, cwd=work, check=True, timeout=600, capture_output=True)
    except (subprocess.SubprocessError, ValueError, OSError):
        out.unlink(missing_ok=True)
        raise HTTPException(500, "Video rendering failed")
    finally:
        sub.unlink(missing_ok=True)
    return {"download_url": f"/editor/{job}/{index}/export/{token}"}

@router.get("/editor/{job}/{index}/export/{token}")
def download(job: str, index: int, token: str):
    path = source(job, index)
    if not re.fullmatch(r"[0-9a-f]{32}", token):
        raise HTTPException(400, "Invalid export")
    out = path.parent / f"edit_{token}.mp4"
    if not out.is_file():
        raise HTTPException(404, "Export not found")
    return FileResponse(out, media_type="video/mp4", filename="optivia-edited.mp4")
