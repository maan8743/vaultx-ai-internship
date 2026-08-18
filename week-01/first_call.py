import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
   model="gemini-3.5-flash-lite", 
    contents="Explain what a token is in one paragraph."
)

print("=== RESPONSE ===")
print(response.text)

print("\n=== TOKEN USAGE ===")
print(f"Input tokens: {response.usage_metadata.prompt_token_count}")
print(f"Output tokens: {response.usage_metadata.candidates_token_count}")
print("\n=== COST ===")
print("Cost: $0.00 (Gemini free tier — no charge for this request)")