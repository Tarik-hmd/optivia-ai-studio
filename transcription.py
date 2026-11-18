from faster_whisper import WhisperModel

model = WhisperModel(
    "tiny",
    device="cpu",
    compute_type="int8"
)


def transcribe_audio(file_path):
    segments, info = model.transcribe(
        file_path,
        language="ar",
        beam_size=5
    )

    transcript_segments = []

    for segment in segments:
        transcript_segments.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip()
        })

    full_text = " ".join(
        segment["text"] for segment in transcript_segments
    )

    return {
        "status": "completed",
        "language": info.language,
        "text": full_text,
        "segments": transcript_segments
    }

    text = " ".join(segment.text.strip() for segment in segments)

    return {
        "status": "completed",
        "language": info.language,
        "text": text
    }