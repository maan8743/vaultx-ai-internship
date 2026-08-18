import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Optional

load_dotenv()


class InvoiceData(BaseModel):
    """All fields Optional — messy real-world text won't always have everything."""
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    total_amount: Optional[float] = None
    due_date: Optional[str] = None
    line_items: Optional[list[str]] = None


def extract_invoice(text: str, model="gemini-3.5-flash-lite", max_retries: int = 3) -> InvoiceData:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""Extract structured invoice data from this text.
If a field is not present in the text, leave it as null — do not guess or invent values.

TEXT:
{text}"""

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=InvoiceData,
                ),
            )
            data = json.loads(response.text)
            return InvoiceData(**data)
        except Exception as e:
            last_error = str(e)
            print(f"[Retry {attempt}/{max_retries}] {last_error}")

    # Never crash — return an empty result with all fields None instead of raising
    print(f"Warning: extraction failed after {max_retries} attempts ({last_error}). Returning empty result.")
    return InvoiceData()


if __name__ == "__main__":
    sample_text = """
    Thanks for your business! Here's a summary of your recent order.
    Invoice #INV-2049
    Vendor: Bright Office Supplies
    Total due: $482.50
    Items: 10x A4 Paper Reams, 5x Toner Cartridges, 2x Desk Organizers
    """

    result = extract_invoice(sample_text)
    print(result.model_dump_json(indent=2))

    # Test with genuinely incomplete text — must NOT crash
    messy_text = "hey we need to settle up for the office chairs sometime this month"
    result2 = extract_invoice(messy_text)
    print(result2.model_dump_json(indent=2))