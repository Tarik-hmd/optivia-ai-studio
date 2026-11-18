
from video_engine import export_vertical_clip

output = export_vertical_clip(
    video_path="test_video.mp4",
    start=0,
    end=10,
    output_path="exports/vertical_test.mp4"
)

print("Vertical clip exported:", output)