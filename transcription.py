
from faster_whisper import WhisperModel


model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)


def transcribe_audio(file_path):
    segments, info = model.transcribe(
        file_path,
        language=None,
        task="transcribe",
        beam_size=5,
        vad_filter=True,
        vad_parameters={
            "min_silence_duration_ms": 500
        },
        condition_on_previous_text=False,
        temperature=0.0
    )

    transcript_segments = []

    for segment in segments:
        text = segment.text.strip()

        if not text:
            continue

        transcript_segments.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": text
        })

    full_text = " ".join(
        segment["text"]
        for segment in transcript_segments
    )

    return {
        "status": "completed",
        "language": info.language,
        "text": full_text,
        "segments": transcript_segments
    }
