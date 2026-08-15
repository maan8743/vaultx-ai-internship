import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()


class GeminiWrapper:
    """
    Reusable wrapper around the Gemini API.
    Handles: sending messages, retries, timeout, token counting, and graceful error handling.
    """

    def __init__(self, model="gemini-3.5-flash-lite", max_retries=3, timeout=30):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment. Check your .env file.")

        # timeout is passed in milliseconds via http_options
        self.client = genai.Client(
            api_key=api_key,
            http_options={"timeout": timeout * 1000}
        )
        self.model = model
        self.max_retries = max_retries
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def send_message(self, prompt, system=None, max_tokens=500, temperature=0.7):
        """
        Sends a prompt to the model. Returns the text response, or a
        clear error message string if something goes wrong — never crashes.
        """
        attempt = 0
        last_error = None

        while attempt < self.max_retries:
            attempt += 1
            try:
                config = {
                    "max_output_tokens": max_tokens,
                    "temperature": temperature,
                }
                if system:
                    config["system_instruction"] = system

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config,
                )

                # token counting
                self.total_input_tokens += response.usage_metadata.prompt_token_count
                self.total_output_tokens += response.usage_metadata.candidates_token_count

                return response.text

            except errors.ClientError as e:
                status = getattr(e, "code", None)

                if status == 401 or status == 403:
                    # invalid key / auth issue — retrying won't help, fail fast
                    return "Error: Invalid API key. Check your .env file."

                elif status == 429:
                    last_error = "Rate limit hit."
                    wait = 2 ** attempt  # exponential backoff: 2s, 4s, 8s...
                    print(f"[Retry {attempt}/{self.max_retries}] {last_error} Waiting {wait}s...")
                    time.sleep(wait)

                elif status == 404:
                    # model name wrong/unavailable — retrying won't help, fail fast
                    return f"Error: model '{self.model}' not found or unavailable. Check the model name."

                else:
                    last_error = f"Client error: {e}"
                    print(f"[Retry {attempt}/{self.max_retries}] {last_error}")
                    time.sleep(2)

            except errors.ServerError as e:
                last_error = f"Server error: {e}"
                print(f"[Retry {attempt}/{self.max_retries}] {last_error}")
                time.sleep(2)

            except errors.APIError as e:
                last_error = f"API error: {e}"
                print(f"[Retry {attempt}/{self.max_retries}] {last_error}")
                time.sleep(2)

        return f"Error: request failed after {self.max_retries} attempts. Last error: {last_error}"

    def get_usage_summary(self):
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
        }


# Quick manual test when run directly
if __name__ == "__main__":
    wrapper = GeminiWrapper()
    reply = wrapper.send_message("Say hello in one sentence.")
    print(reply)
    print(wrapper.get_usage_summary())