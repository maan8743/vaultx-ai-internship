import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Literal
import json

load_dotenv()


class ClassificationResult(BaseModel):
    category: Literal["billing", "technical", "account", "feature_request", "complaint", "other"]
    priority: Literal["low", "medium", "high", "urgent"]
    sentiment: Literal["positive", "neutral", "negative"]
    needs_human: bool


def classify_message(message: str, model="gemini-3.5-flash-lite", max_retries: int = 3) -> ClassificationResult:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""Classify this customer support message.

MESSAGE:
{message}

Return category, priority, sentiment, and whether it needs human review (needs_human)."""

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ClassificationResult,
                ),
            )
            data = json.loads(response.text)
            return ClassificationResult(**data)
        except Exception as e:
            last_error = str(e)
            print(f"[Retry {attempt}/{max_retries}] {last_error}")

    raise ValueError(f"Classification failed after {max_retries} attempts: {last_error}")


# 20 realistic test samples
TEST_MESSAGES = [
    "My card was charged twice for the same order, please refund immediately!",
    "The app crashes every time I try to upload a photo.",
    "I love the new dashboard redesign, great work!",
    "How do I reset my password? I can't find the option anywhere.",
    "This is the third time I'm contacting support about the same bug. Fix it now.",
    "Can you add dark mode to the mobile app?",
    "I was overcharged on my invoice this month.",
    "Your service has been down for 3 hours, my whole team can't work.",
    "Just wanted to say thanks, the support team was super helpful yesterday.",
    "I can't log in, it says my account is locked.",
    "Please cancel my subscription and refund the remaining balance.",
    "The export feature is missing columns compared to last month.",
    "Is there a way to integrate this with Slack?",
    "I'm extremely frustrated, this is the worst customer experience I've had.",
    "Quick question — what's your refund policy?",
    "The API returns a 500 error on every request since this morning.",
    "Love the product overall, just wish there were more themes.",
    "My data seems to have disappeared after the last update, I need this fixed urgently.",
    "Can someone explain how billing cycles work for annual plans?",
    "Everything works great, no complaints here!",
]


if __name__ == "__main__":
    results = []
    for i, msg in enumerate(TEST_MESSAGES, 1):
        result = classify_message(msg)
        results.append((msg, result))
        print(f"\n[{i}] {msg}")
        print(f"    -> {result.model_dump()}")

    # Save results to a file for your report
    with open("classification_results.txt", "w", encoding="utf-8") as f:
        for i, (msg, result) in enumerate(results, 1):
            f.write(f"[{i}] {msg}\n")
            f.write(f"    Category: {result.category}\n")
            f.write(f"    Priority: {result.priority}\n")
            f.write(f"    Sentiment: {result.sentiment}\n")
            f.write(f"    Needs human: {result.needs_human}\n\n")