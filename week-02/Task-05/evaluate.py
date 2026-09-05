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


# 15 test cases with known correct answers
EVAL_SET = [
    ("I absolutely love this product, best purchase ever!", "positive"),
    ("This is garbage, complete waste of money.", "negative"),
    ("It's fine, does what it says.", "neutral"),
    ("Worst customer service I've ever experienced.", "negative"),
    ("Exceeded my expectations in every way.", "positive"),
    ("Not bad, not great, just okay.", "neutral"),
    ("I'm never buying from this company again.", "negative"),
    ("Pretty happy with how this turned out.", "positive"),
    ("It arrived on time, nothing special to report.", "neutral"),
    ("Absolutely thrilled with the results!", "positive"),
    ("Disappointed — it broke after two days.", "negative"),
    ("Average product for the price.", "neutral"),
    ("This changed my life, incredible!", "positive"),
    ("Terrible experience from start to finish.", "negative"),
    ("It works as described, nothing more.", "neutral"),
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
        mark = "✓" if is_correct else "✗"
        print(f"  {mark} expected={expected:8s} got={predicted:8s} | {text}")

    return accuracy, results


# Version 1: bare-bones prompt (baseline)
def prompt_v1(text):
    return f"What is the sentiment of: {text}"


# Version 2: improved — clearer instruction, explicit categories, neutral guidance
def prompt_v2(text):
    return f"""Classify the sentiment of this text as exactly one of: positive, negative, or neutral.

Guidance: use "neutral" only for genuinely balanced/factual statements with no clear
positive or negative lean — do not default to neutral just because a statement is short.

TEXT: {text}"""


if __name__ == "__main__":
    acc_v1, _ = run_eval(prompt_v1, "Prompt V1 (baseline)")

    print("\nWaiting 30 seconds before starting V2 to avoid rate limit...")
    time.sleep(30)

    acc_v2, _ = run_eval(prompt_v2, "Prompt V2 (improved)")

    print(f"\n=== IMPROVEMENT ===")
    print(f"V1: {acc_v1:.1f}%  ->  V2: {acc_v2:.1f}%  (change: {acc_v2 - acc_v1:+.1f} points)")

    with open("evaluation_results.txt", "w", encoding="utf-8") as f:
        f.write(f"Prompt V1 accuracy: {acc_v1:.1f}%\n")
        f.write(f"Prompt V2 accuracy: {acc_v2:.1f}%\n")
        f.write(f"Improvement: {acc_v2 - acc_v1:+.1f} points\n")