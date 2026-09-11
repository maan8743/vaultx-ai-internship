import os
import json
import time
import argparse
import sys
from log_expense import log_to_sheet
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError
from typing import Literal, Optional

load_dotenv()


class ReceiptData(BaseModel):
    merchant: str
    date: str
    total: float
    category: Literal[
        "groceries", "dining", "transport", "shopping",
        "utilities", "entertainment", "other"
    ]
    line_items: Optional[list[str]] = None
    confidence: Literal["high", "medium", "low"]


RECEIPT_PROMPT = """Extract structured data from this receipt.

Categorize it as exactly one of: groceries, dining, transport, shopping,
utilities, entertainment, other.

Rate your own confidence as "high", "medium", or "low" based on how clear
and complete the receipt is.

If the total or date is genuinely unclear or missing, do your best estimate
but mark confidence as "low"."""


def _call_gemini_with_retry(client, contents, model, max_retries):
    """Shared retry logic for both text and image extraction paths."""
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ReceiptData,
                ),
            )
            data = json.loads(response.text)
            return ReceiptData(**data)

        except (json.JSONDecodeError, ValidationError) as e:
            last_error = str(e)
            print(f"[Retry {attempt}/{max_retries}] Invalid response: {last_error}")
            time.sleep(2)

        except Exception as e:
            last_error = f"{type(e).__name__}: {e}"
            wait = 2 ** attempt
            print(f"[Retry {attempt}/{max_retries}] Network/API error: {last_error}. Waiting {wait}s...")
            time.sleep(wait)

    raise ValueError(f"Failed to extract receipt after {max_retries} attempts: {last_error}")


def extract_receipt(receipt_text: str, model="gemini-3.5-flash-lite", max_retries: int = 4) -> ReceiptData:
    """Extract structured data from typed/pasted receipt TEXT."""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = f"{RECEIPT_PROMPT}\n\nRECEIPT TEXT:\n{receipt_text}"
    return _call_gemini_with_retry(client, prompt, model, max_retries)


def extract_receipt_from_image(image_path: str, model="gemini-3.5-flash-lite", max_retries: int = 4) -> ReceiptData:
    """Extract structured data directly from a photo of a receipt — Gemini reads the image natively."""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    ext = image_path.lower().split(".")[-1]
    mime_type = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"

    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    contents = [image_part, RECEIPT_PROMPT]

    return _call_gemini_with_retry(client, contents, model, max_retries)


def get_receipt_text(args):
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            return f.read()
    elif args.text:
        return args.text
    else:
        print("Error: provide --file <path>, --text \"receipt text here\", or --image <path>")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract structured data from a receipt (text, file, or image)."
    )
    parser.add_argument("--file", help="Path to a text file containing the receipt")
    parser.add_argument("--text", help="Receipt text passed directly on the command line")
    parser.add_argument("--image", help="Path to a photo of a receipt (jpg/png)")
    args = parser.parse_args()

    if args.image:
        result = extract_receipt_from_image(args.image)
        source = "gallery_or_camera_image"
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            receipt_text = f.read()
        result = extract_receipt(receipt_text)
        source = "text_file"
    elif args.text:
        result = extract_receipt(args.text)
        source = "typed_text"
    else:
        print("Error: provide --file <path>, --text \"receipt text here\", or --image <path>")
        sys.exit(1)

    print(result.model_dump_json(indent=2))
    log_to_sheet(result, source=source)