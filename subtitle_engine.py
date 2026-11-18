
def format_srt_time(seconds):
    milliseconds = round(seconds * 1000)

    hours = milliseconds // 3600000
    minutes = (milliseconds % 3600000) // 60000
    secs = (milliseconds % 60000) // 1000
    ms = milliseconds % 1000

    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def generate_srt(segments, output_path):
    with open(output_path, "w", encoding="utf-8") as file:
        for index, segment in enumerate(segments, start=1):
            start = format_srt_time(segment["start"])
            end = format_srt_time(segment["end"])
            text = segment["text"].strip()

            file.write(f"{index}\n")
            file.write(f"{start} --> {end}\n")
            file.write(f"{text}\n\n")

    return output_path


def get_clip_segments(segments, clip_start, clip_end):
    clip_segments = []

    for segment in segments:
        start = max(segment["start"], clip_start)
        end = min(segment["end"], clip_end)

        if start >= end:
            continue

        clip_segments.append({
            "start": round(start - clip_start, 3),
            "end": round(end - clip_start, 3),
            "text": segment["text"]
        })

    return clip_segments

   

