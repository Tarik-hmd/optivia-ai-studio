from pydantic import BaseModel, Field, StrictInt
from openai import OpenAI
from semantic_scoring import calculate_semantic_score
from semantic_scoring import rank_clips

def build_scoring_prompt(transcript):
    return f"""
You are an expert short-form video editor.

Analyze the following transcript and evaluate
its potential as a viral short-form clip.

TRANSCRIPT:
{transcript}

Evaluate these four criteria from 0 to 5:

1. hook: How attention-grabbing is the opening?
2. clarity: Can the clip be understood alone?
3. emotion: Does it trigger an emotional reaction?
4. value: Does it provide useful or interesting content?

Return ONLY a JSON object with:
- hook
- clarity
- emotion
- value
- reason
"""


class ClipEvaluation(BaseModel):
    hook: StrictInt = Field(ge=0, le=5)
    clarity: StrictInt = Field(ge=0, le=5)
    emotion: StrictInt = Field(ge=0, le=5)
    value: StrictInt = Field(ge=0, le=5)
    reason: str


def create_llm_client(api_key):
    return OpenAI(api_key=api_key)


def evaluate_clip(client, transcript):
    prompt = build_scoring_prompt(transcript)

    response = client.responses.parse(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        text_format=ClipEvaluation
    )

    return response.output_parsed


def score_clip(client, transcript):
    evaluation = evaluate_clip(client, transcript)

    total_score = calculate_semantic_score(
        evaluation.hook,
        evaluation.clarity,
        evaluation.emotion,
        evaluation.value
    )

    return {
        "score": total_score,
        "evaluation": evaluation.model_dump()
    }


def evaluate_candidates(client, candidates, top_n=5):
    evaluated_clips = []

    for candidate in candidates:
        result = score_clip(
            client,
            candidate["text"]
        )

        evaluated_clips.append({
            **candidate,
            "keyword_score": candidate.get("score", 0),
            "score": result["score"],
            "evaluation": result["evaluation"]
        })

    return rank_clips(evaluated_clips, top_n)
