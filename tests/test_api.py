
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_reject_invalid_extension():
    response = client.post(
        "/process-video",
        files={
            "file": (
                "document.txt",
                b"This is not a video",
                "text/plain"
            )
        }
    )


def test_reject_fake_mp4():
    response = client.post(
        "/process-video",
        files={
            "file": (
                "fake_video.mp4",
                b"This is not a real video",
                "video/mp4"
            )
        }
    )

    assert response.status_code == 400


def test_reject_oversized_video(monkeypatch):
    monkeypatch.setattr("api.MAX_UPLOAD_SIZE", 10)

    response = client.post(
        "/process-video",
        files={
            "file": (
                "video.mp4",
                b"This file is larger than ten bytes",
                "video/mp4"
            )
        }
    )

    assert response.status_code == 413


def test_temp_file_cleanup(monkeypatch, tmp_path):
    import api

    created_files = []
    original_temp_file = api.tempfile.NamedTemporaryFile

    def tracked_temp_file(*args, **kwargs):
        kwargs["dir"] = tmp_path
        temp_file = original_temp_file(*args, **kwargs)
        created_files.append(temp_file.name)
        return temp_file

    monkeypatch.setattr(
        api.tempfile,
        "NamedTemporaryFile",
        tracked_temp_file
    )

    response = client.post(
        "/process-video",
        files={
            "file": (
                "fake.mp4",
                b"Invalid video content",
                "video/mp4"
            )
        }
    )

    assert response.status_code == 400
    assert len(created_files) == 1
    assert not (tmp_path / "fake.mp4").exists()
    assert not list(tmp_path.iterdir())


def test_mock_video_validation(monkeypatch):
    import api

    def fake_validate_video(video_path):
        return False

    monkeypatch.setattr(
        api,
        "validate_video",
        fake_validate_video
    )

    response = client.post(
        "/process-video",
        files={
            "file": (
                "test.mp4",
                b"fake video content",
                "video/mp4"
            )
        }
    )

    assert response.status_code == 400


def test_mock_transcription(monkeypatch):
    import api

    def fake_validate_video(video_path):
        return True

    def fake_transcribe_audio(audio_path):
        return {
            "segments": [
                {
                    "start": 0.0,
                    "end": 15.0,
                    "text": "The secret to success is consistency."
                },
                {
                    "start": 15.0,
                    "end": 30.0,
                    "text": "Never give up on your goals."
                }
            ]
        }

    monkeypatch.setattr(
        api, "validate_video", fake_validate_video
    )

    monkeypatch.setattr(
        api, "transcribe_audio", fake_transcribe_audio
    )

    monkeypatch.setattr(
        api, "build_clips", lambda *args, **kwargs: []
    )

    response = client.post(
        "/process-video",
        files={
            "file": (
                "test.mp4",
                b"fake video content",
                "video/mp4"
            )
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["transcription"]["segments"]) == 2
    assert data["clips"] == []


def test_mock_video_export(monkeypatch, tmp_path):
    import api

    def fake_export_vertical_clip(
        video_path, start, end, output_path
    ):
        from pathlib import Path

        Path(output_path).write_bytes(b"fake vertical video")

    monkeypatch.setattr(
        api,
        "export_vertical_clip",
        fake_export_vertical_clip
    )

    output_path = tmp_path / "vertical_clip_1.mp4"

    api.export_vertical_clip(
        video_path="input.mp4",
        start=10,
        end=30,
        output_path=str(output_path)
    )

    assert output_path.exists()
    assert output_path.read_bytes() == b"fake vertical video"


def test_full_pipeline_with_mocks(monkeypatch, tmp_path):
    import api
    from pathlib import Path

    # Isolate exported files in a temporary directory
    
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(
        api,
        "EXPORT_DIR",
        tmp_path / "exports"
    )

    monkeypatch.setattr(
        api, "validate_video",
        lambda path: True
    )

    monkeypatch.setattr(
        api, "transcribe_audio",
        lambda path: {
            "segments": [
                {
                    "start": 0.0,
                    "end": 20.0,
                    "text": "The secret to success is consistency."
                }
            ]
        }
    )

    monkeypatch.setattr(
        api, "build_clips",
        lambda *args, **kwargs: [
            {
                "start": 0.0,
                "end": 20.0,
                "duration": 20.0,
                "score": 8
            }
        ]
    )

    def fake_export(video_path, start, end, output_path):
        Path(output_path).parent.mkdir(
            parents=True, exist_ok=True
        )
        Path(output_path).write_bytes(b"vertical video")

    def fake_subtitles(video_path, subtitle_path, output_path):
        Path(output_path).write_bytes(b"final video")

    def fake_srt(segments, subtitle_path):
        Path(subtitle_path).write_text("fake subtitles")

    monkeypatch.setattr(api, "export_vertical_clip", fake_export)
    monkeypatch.setattr(api, "add_subtitles", fake_subtitles)
    monkeypatch.setattr(api, "generate_srt", fake_srt)

    response = client.post(
        "/process-video",
        files={
            "file": ("test.mp4", b"fake mp4", "video/mp4")
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["clips"]) == 1
    assert data["clips"][0]["score"] == 8
    assert data["clips"][0]["download_url"].endswith(
        "/final_clip_1.mp4"
    )

    download_url = data["clips"][0]["download_url"]

    download_response = client.get(download_url)

    assert download_response.status_code == 200
    assert download_response.content == b"final video"


def test_download_invalid_job_id():
    response = client.get(
        "/download/invalid-id/final_clip_1.mp4"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid job ID"


def test_download_invalid_filename():
    valid_job_id = "a" * 32

    response = client.get(
        f"/download/{valid_job_id}/secret.mp4"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid filename"
