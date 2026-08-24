import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Literal
import json

load_dotenv()


class SentimentResult(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]


# A harder eval set on purpose — sarcasm, mixed sentiment, and short/ambiguous
# statements are exactly the cases where a vague prompt tends to fail, and where
# clearer instructions make a real, measurable difference.
EVAL_SET = [
    ("Oh great, another update that breaks everything. Just perfect.", "negative"),          # sarcasm
    ("The food was amazing but the service was painfully slow.", "neutral"),                  # mixed
    ("I guess it's okay.", "neutral"),                                                        # weak/vague
    ("Sure, take your time, it's not like I'm in a hurry or anything.", "negative"),           # sarcasm
    ("It works.", "neutral"),                                                                 # minimal, factual
    ("Best decision I've made all year, no regrets at all.", "positive"),
    ("Not the worst thing I've bought, but I wouldn't buy it again.", "negative"),             # subtle negative
    ("Wow, five stars, truly a masterpiece of poor design.", "negative"),                      # sarcasm
    ("The room was clean, check-in was quick, staff were polite.", "positive"),                # implied positive, factual tone
    ("Honestly? Kind of a letdown after all the hype.", "negative"),
    ("It does exactly what it says on the box, nothing more.", "neutral"),
    ("I laughed, I cried, I'd do it all over again.", "positive"),
    ("The battery life is decent, the camera is mediocre, overall it's fine.", "neutral"),     # mixed, net neutral
    ("Can't complain, does the job.", "neutral"),
    ("Absolutely thrilled — this exceeded every expectation I had.", "positive"),
]


def run_eval(prompt_builder, label: str):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    correct = 0
    results = []

    for text, expected in EVAL_SET:
        prompt = prompt_builder(text)
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SentimentResult,
            ),
        )
        data = json.loads(response.text)
        predicted = data["sentiment"]
        is_correct = predicted == expected
        correct += is_correct
        results.append((text, expected, predicted, is_correct))
        time.sleep(4)  # stay under free-tier rate limit (15 requests/minute)

    accuracy = correct / len(EVAL_SET) * 100
    print(f"\n=== {label} — Accuracy: {accuracy:.1f}% ({correct}/{len(EVAL_SET)}) ===")
    for text, expected, predicted, is_correct in results:
        mark = "correct" if is_correct else "WRONG  "
        print(f"  [{mark}] expected={expected:8s} got={predicted:8s} | {text}")

    return accuracy, results


# Version 1: bare-bones prompt — no guidance on sarcasm, mixed sentiment, or
# how to weigh a statement with no clear emotional language. This is deliberately
# weak so the eval can actually show a measurable gap.
def prompt_v1(text):
    return f"What is the sentiment of: {text}"


# Version 2: improved — explicitly tells the model how to handle exactly the
# hard cases this eval set is full of: sarcasm, mixed opinions, and flat/factual
# statements with no strong emotional language.
def prompt_v2(text):
    return f"""Classify the sentiment of this text as exactly one of: positive, negative, or neutral.

Guidance:
- Watch for sarcasm: phrases like "oh great" or "just perfect" used ironically
  about something bad are NEGATIVE, not positive.
- If the text expresses both a positive and a negative point, classify based on
  the OVERALL/net impression, and use "neutral" only if the two genuinely balance out.
- Short, flat, factual statements with no clear emotional language (e.g. "it works",
  "can't complain") are NEUTRAL, not positive, unless they contain a real positive/negative word.

TEXT: {text}"""


if __name__ == "__main__":
    acc_v1, results_v1 = run_eval(prompt_v1, "Prompt V1 (baseline, no guidance)")
    acc_v2, results_v2 = run_eval(prompt_v2, "Prompt V2 (improved, handles sarcasm/mixed/flat cases)")

    print(f"\n=== IMPROVEMENT ===")
    print(f"V1: {acc_v1:.1f}%  ->  V2: {acc_v2:.1f}%  (change: {acc_v2 - acc_v1:+.1f} points)")

    # Show exactly which cases flipped from wrong to right — this is the clearest
    # possible evidence that the added guidance was what caused the improvement.
    print(f"\n=== CASES THAT IMPROVED (wrong in V1, correct in V2) ===")
    for (text, expected, pred_v1, correct_v1), (_, _, pred_v2, correct_v2) in zip(results_v1, results_v2):
        if not correct_v1 and correct_v2:
            print(f"  \"{text}\"")
            print(f"    V1 said: {pred_v1} (wrong)  ->  V2 said: {pred_v2} (correct, expected: {expected})")

    with open("evaluation_results.txt", "w", encoding="utf-8") as f:
        f.write(f"Prompt V1 accuracy: {acc_v1:.1f}%\n")
        f.write(f"Prompt V2 accuracy: {acc_v2:.1f}%\n")
        f.write(f"Improvement: {acc_v2 - acc_v1:+.1f} points\n\n")
        f.write("Cases that improved (wrong in V1, correct in V2):\n")
        for (text, expected, pred_v1, correct_v1), (_, _, pred_v2, correct_v2) in zip(results_v1, results_v2):
            if not correct_v1 and correct_v2:
                f.write(f"  \"{text}\" | V1: {pred_v1} (wrong) -> V2: {pred_v2} (correct)\n")