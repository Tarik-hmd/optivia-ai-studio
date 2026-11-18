
from video_engine import export_clip

export_clip(
    video_path="test_video.mp4",
    start=5,
    end=15,
    output_path="exports/clip_1.mp4"
)

print("Video exported successfully!")

