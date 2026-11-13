from transcription import transcribe_audio

result = transcribe_audio("test.mp3")

print("Language:", result["language"])
print("Transcript:", result["text"])