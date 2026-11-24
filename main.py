
# OPTIVIA AI STUDIO
# Version 1.0 - Transcript Analyzer
from semantic_scoring import rank_clips
from scoring import calculate_score


      

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
    ranked_clips = rank_clips(
        potential_clips,
        top_n=None
    )

    return {
        "word_count": total_words,
        "character_count": character_count,
        "sentence_count": sentence_count,
        "potential_clips": potential_clips,
        "ranked_clips": ranked_clips
    }