import os
import csv
import io
import requests
from dotenv import load_dotenv
from google import genai

load_dotenv()

SHEET_ID = "1zP3f8kqfGmV-iZWd74YgjlTRfopNN8mscLinPd3JZLI"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"


def fetch_expenses():
    """Pull the current sheet data as a list of dicts, with normalized column names
    (lowercase, stripped of extra whitespace) so header formatting quirks in the
    actual Google Sheet don't break the lookups."""
    response = requests.get(SHEET_CSV_URL, timeout=10)
    response.raise_for_status()

    reader = csv.DictReader(io.StringIO(response.text))
    rows = []
    for row in reader:
        normalized_row = {key.strip().lower(): (value or "").strip() for key, value in row.items()}
        rows.append(normalized_row)
    return rows


def answer_question(question: str):
    expenses = fetch_expenses()

    if not expenses:
        return "No expense data found yet — log a few receipts first."

    rows_text = "\n".join(
        f"{row.get('date','')} | {row.get('merchant','')} | {row.get('category','')} | "
        f"${row.get('total','')} | {row.get('line_items','')}"
        for row in expenses
    )

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""You are a personal finance assistant. Answer the question using ONLY
the expense data below. Do actual math where needed (sums, counts, comparisons).
If the data doesn't contain enough information to answer, say so honestly.

EXPENSE DATA (date | merchant | category | total | items):
{rows_text}

QUESTION: {question}

ANSWER:"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )
    return response.text


if __name__ == "__main__":
    while True:
        question = input("\nAsk about your spending (or 'quit'): ")
        if question.lower() == "quit":
            break
        print(f"\n{answer_question(question)}")