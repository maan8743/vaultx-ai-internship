import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT = "Write one sentence describing a sunset."
TEMPERATURES = [0.0, 0.7, 1.0]
results = {}

for temp in TEMPERATURES:
    results[temp] = []
    for i in range(3):
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=PROMPT,
            config={"temperature": temp, "max_output_tokens": 100}
        )
        text = response.text.strip()
        results[temp].append(text)
        print(f"[temp={temp}, run={i+1}] {text}\n")

# Save raw results to a file so you can build your table from it
with open("temperature_results.txt", "w", encoding="utf-8") as f:
    for temp, outputs in results.items():
        f.write(f"\n--- Temperature {temp} ---\n")
        for i, out in enumerate(outputs, 1):
            f.write(f"Run {i}: {out}\n")