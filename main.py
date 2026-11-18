
# OPTIVIA AI STUDIO
# Version 1.0 - Transcript Analyzer
from scoring import calculate_score
transcript = """
Most people think that success comes from working harder.
But I believe it comes from building better systems.
If you want to grow your business, stop trying to do everything yourself.
Focus on creating processes that work without you.
The biggest mistake entrepreneurs make is waiting until they feel ready.
Start before you are ready, learn from your mistakes, and improve every single day.
"""


      

# 1. ANALYZE TRANSCRIPT

def analyze_transcript(text, min_words=8, max_words=25):

    total_words = len(text.split())
    character_count = len(text)

    sentences = text.split(".")
    sentence_count = 0
    potential_clips = []

    for sentence in sentences:
        clean_sentence = sentence.strip()

        if clean_sentence:
            sentence_count += 1
            word_count = len(clean_sentence.split())

            if min_words <= word_count <= max_words:

                score = calculate_score(clean_sentence)

                # Create clip dictionary
                clip = {
                    "text": clean_sentence,
                    "word_count": word_count,
                    "status": "selected",
                    "score": score
                }

                potential_clips.append(clip)

    # Rank clips by score
    ranked_clips = sorted(
        potential_clips,
        key=lambda clip: clip["score"],
        reverse=True
    )

    return {
        "word_count": total_words,
        "character_count": character_count,
        "sentence_count": sentence_count,
        "potential_clips": potential_clips,
        "ranked_clips": ranked_clips
    }


# 2. GET TOP CLIPS


# 4. RUN OPTIVIA

if __name__ == "__main__":
    result = analyze_transcript(transcript)

    print("===== OPTIVIA AI STUDIO =====")
    print(f"Total words: {result['word_count']}")
    print(f"Characters: {result['character_count']}")
    print(f"Sentences: {result['sentence_count']}")
    print(f"Clips detected: {count_clips(result['potential_clips'])}")

    print("\n===== TOP 3 CLIPS =====")

    top_clips = get_top_clips(result["ranked_clips"], 3)

    for clip in top_clips:
        print(f"Clip: {clip['text']}")
        print(f"Words: {clip['word_count']}")
        print(f"Status: {clip['status']}")
        print(f"Score: {clip['score']}")
        print("--------------------")

    assert calculate_score("Never reveal the secret to success!") == 8
    assert calculate_score("How can I avoid this mistake?") == 4
    assert calculate_score("Hello everyone!") == 0

    print("All tests passed!")
