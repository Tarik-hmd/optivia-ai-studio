
import subprocess
from pathlib import Path
import json
import subprocess


def export_clip(video_path, start, end, output_path):
    duration = end - start

    if duration <= 0:
        raise ValueError("Clip duration must be positive")

    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    command = [
        "ffmpeg",
        "-y",
        "-ss", str(start),
        "-i", str(video_path),
        "-t", str(duration),
        "-c:v", "libx264",
        "-c:a", "aac",
        str(output_path)
    ]

    subprocess.run(command, check=True)

    return str(output_path)


def export_vertical_clip(video_path, start, end, output_path):
    duration = end - start

    if duration <= 0:
        raise ValueError("Clip duration must be positive")

    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    command = [
        "ffmpeg",
        "-y",
        "-ss", str(start),
        "-i", str(video_path),
        "-t", str(duration),

        # Crop to vertical 9:16
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "setsar=1",

        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-movflags", "+faststart",

        str(output_path)
    ]

    subprocess.run(command, check=True)

    return str(output_path)


def add_subtitles(video_path, subtitle_path, output_path):
    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # FFmpeg requires forward slashes and escaped drive colon
    subtitle_file = Path(subtitle_path).resolve().as_posix()
    subtitle_file = subtitle_file.replace(":", r"\:")

    subtitle_filter = (
        f"subtitles=filename='{subtitle_file}':"
        "force_style='FontName=Arial,"
        "FontSize=16,"
        "PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,"
        "BorderStyle=1,"
        "Outline=2,"
        "Alignment=2,"
        "MarginV=160'"
    )

    command = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-vf", subtitle_filter,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        str(output_path)
    ]

    subprocess.run(command, check=True)

    return str(output_path)


def validate_video(video_path):
    command = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=codec_type",
        "-of", "json",
        str(video_path)
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )

        data = json.loads(result.stdout)
        streams = data.get("streams", [])

        return any(
            stream.get("codec_type") == "video"
            for stream in streams
        )

    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        json.JSONDecodeError
    ):
        return False
