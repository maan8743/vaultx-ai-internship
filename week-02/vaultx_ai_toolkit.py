"""
VaultX AI Toolkit — reusable, logged module wrapping Week 02's structured-output tools.
Import this in future weeks instead of rewriting classification/extraction logic.
"""
import os
import json
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError
from typing import Literal, Optional, Type, TypeVar

load_dotenv()

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("vaultx_ai_toolkit.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("vaultx_ai_toolkit")

T = TypeVar("T", bound=BaseModel)


# --- Schemas ---
class ClassificationResult(BaseModel):
    category: Literal["billing", "technical", "account", "feature_request", "complaint", "other"]
    priority: Literal["low", "medium", "high", "urgent"]
    sentiment: Literal["positive", "neutral", "negative"]
    needs_human: bool


class InvoiceData(BaseModel):
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    total_amount: Optional[float] = None
    due_date: Optional[str] = None
    line_items: Optional[list[str]] = None


# --- Core engine ---
class VaultXAIToolkit:
    def __init__(self, model: str = "gemini-3.5-flash-lite", max_retries: int = 3):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment.")
            raise ValueError("GEMINI_API_KEY not found in environment. Check your .env file.")

        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.max_retries = max_retries
        logger.info(f"VaultXAIToolkit initialized with model={model}")

    def _get_structured(self, prompt: str, schema: Type[T]) -> Optional[T]:
        """Internal helper: call the model, validate against schema, retry on failure, log everything."""
        current_prompt = prompt
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=current_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema,
                    ),
                )
                data = json.loads(response.text)
                validated = schema(**data)
                logger.info(f"Success on attempt {attempt} for schema={schema.__name__}")
                return validated

            except (json.JSONDecodeError, ValidationError) as e:
                logger.warning(f"Attempt {attempt}/{self.max_retries} failed validation: {e}")
                current_prompt = f"{prompt}\n\nPrevious response was invalid: {e}\nReturn ONLY valid JSON."

            except Exception as e:
                logger.error(f"Attempt {attempt}/{self.max_retries} unexpected error: {e}")

        logger.error(f"All {self.max_retries} attempts failed for schema={schema.__name__}. Returning None.")
        return None

    def classify_message(self, message: str) -> Optional[ClassificationResult]:
        """Classify a support message. Returns None (never raises) if classification fails."""
        prompt = f"""Classify this customer support message.

MESSAGE:
{message}

Return category, priority, sentiment, and needs_human."""
        return self._get_structured(prompt, ClassificationResult)

    def extract_invoice(self, text: str) -> InvoiceData:
        """Extract invoice fields. Always returns an InvoiceData — missing fields are None, never raises."""
        prompt = f"""Extract structured invoice data from this text.
If a field is not present, leave it null — do not guess.

TEXT:
{text}"""
        result = self._get_structured(prompt, InvoiceData)
        return result if result is not None else InvoiceData()


# Quick self-test when run directly
if __name__ == "__main__":
    toolkit = VaultXAIToolkit()

    print("=== Classification ===")
    result = toolkit.classify_message("My payment failed twice and I need this fixed today.")
    print(result)

    print("\n=== Extraction ===")
    invoice = toolkit.extract_invoice("Invoice #A102, Vendor: Acme Corp, Total: $150.00")
    print(invoice)