
from video_engine import add_subtitles

output = add_subtitles(
    video_path="exports/vertical_clip_1.mp4",
    subtitle_path="exports/test_subtitles.srt",
    output_path="exports/final_subtitled.mp4"
)

print("Subtitled video exported:", output)
