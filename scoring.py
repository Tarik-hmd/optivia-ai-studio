
import string
import unicodedata

KEYWORDS = {
    # English
    "success": 2,
    "mistake": 3,
    "secret": 4,
    "never": 2,
    "how": 1,

    # French
    "réussite": 2,
    "succès": 2,
    "erreur": 3,
    "secret": 4,
    "jamais": 2,
    "comment": 1,

    # Arabic
    "النجاح": 2,
    "خطأ": 3,
    "سر": 4,
    "أبداً": 2,
    "كيف": 1,
}


SYNONYM_GROUPS = {
    "mistake": {"mistake", "error", "erreur", "faute", "خطأ"},
}


def normalize_accents(word):
    return "".join(
        character
        for character in unicodedata.normalize("NFD", word)
        if unicodedata.category(character) != "Mn"
    )


def normalize_arabic_word(word):
    if word.startswith("ال") and len(word) > 2:
        return word[2:]

    return word


def calculate_score(sentence):
    words = sentence.lower().split()

    clean_words = [
        word.strip(string.punctuation + "؟،؛«»")
        for word in words
    ]

    score = 0

    normalized_words = {
        normalize_accents(normalize_arabic_word(word))
        for word in clean_words
    }


    matched_groups = set()


    for keyword, points in KEYWORDS.items():
        normalized_keyword = normalize_accents(
            normalize_arabic_word(keyword)
        )

        group_name = next(
            (
                name
                for name, synonyms in SYNONYM_GROUPS.items()
                if keyword in synonyms

            ),

            keyword
        )

        if group_name in matched_groups:
            continue

        group_words = SYNONYM_GROUPS.get(
            group_name, {keyword}
        )  
        normalized_group = {
            
            normalize_accents(normalize_arabic_word(word))
            for word in group_words


        }

        if normalized_words & normalized_group:
            score += points
            matched_groups.add(group_name)

    if sentence.strip().endswith(("?", "؟")):
        score += 2

    return min(score, 10)

