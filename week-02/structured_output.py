import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError

load_dotenv()


class Person(BaseModel):
    """Example schema — swap this for whatever structure you need."""
    name: str
    age: int
    occupation: str


def get_structured_response(prompt: str, schema: type[BaseModel], model="gemini-3.5-flash-lite", max_retries: int = 3):
    """
    Sends a prompt, forces JSON output matching `schema`, validates it with Pydantic,
    and retries (with the error fed back to the model) if validation fails.
    Returns a validated Pydantic instance, or raises ValueError after max_retries.
    """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    current_prompt = prompt
    last_error = None

    for attempt in range(1, max_retries + 1):
        response = client.models.generate_content(
            model=model,
            contents=current_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )

        raw_text = response.text

        try:
            # Gemini already tries to conform to the schema, but we validate
            # ourselves too — never trust an external API blindly.
            data = json.loads(raw_text)
            validated = schema(**data)
            return validated

        except (json.JSONDecodeError, ValidationError) as e:
            last_error = str(e)
            print(f"[Retry {attempt}/{max_retries}] Invalid JSON/schema: {last_error}")
            # Feed the error back so the model can self-correct next attempt
            current_prompt = (
                f"{prompt}\n\nYour previous response was invalid: {last_error}\n"
                f"Return ONLY valid JSON matching the required schema."
            )

    raise ValueError(f"Failed to get valid structured output after {max_retries} attempts. Last error: {last_error}")


if __name__ == "__main__":
    result = get_structured_response(
        "Generate a fictional person who works in cybersecurity.",
        Person
    )
    print(result)
    print(result.model_dump_json(indent=2))