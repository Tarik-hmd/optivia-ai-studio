from faster_whisper import WhisperModel

model = WhisperModel(
    "tiny",
    device="cpu",
    compute_type="int8"
)

def transcribe_audio(file_path):
    segments, info = model.transcribe(
    file_path,
    language="ar"
)
    text = " ".join(segment.text.strip() for segment in segments)

    return {
        "status": "completed",
        "language": info.language,
        "text": text
    }