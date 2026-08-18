import argparse
import sys
from api_wrapper import GeminiWrapper


def get_input_text(args):
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            return f.read()
    elif args.text:
        return args.text
    else:
        print("Error: provide --file <path> or --text \"your text here\"")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Summarize a block of text: summary, key points, and sentiment."
    )
    parser.add_argument("--file", help="Path to a text file")
    parser.add_argument("--text", help="Text passed directly on the command line")
    args = parser.parse_args()

    content = get_input_text(args)

    wrapper = GeminiWrapper()

    prompt = f"""Analyze the following text and return:
1. A concise summary (2-3 sentences)
2. Key points (bullet list)
3. Overall sentiment (positive/negative/neutral, with one-line reasoning)

TEXT:
{content}
"""

    result = wrapper.send_message(prompt, max_tokens=500)
    print("\n=== ANALYSIS ===\n")
    print(result)
    print("\n=== TOKEN USAGE ===")
    print(wrapper.get_usage_summary())


if __name__ == "__main__":
    main()