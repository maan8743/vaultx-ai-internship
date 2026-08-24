"""
Reusable prompt template library — Week 02 Task 01.
Each function returns a ready-to-send prompt (or system+prompt pair) demonstrating one pattern.
"""


def zero_shot(question: str) -> str:
    """Ask directly, no examples, no extra structure."""
    return question


def few_shot(examples: list[tuple[str, str]], new_input: str) -> str:
    """
    examples: list of (input, output) pairs the model learns from.
    new_input: the real input you want answered, following the same pattern.
    """
    prompt = "Follow the pattern shown in these examples:\n\n"
    for inp, out in examples:
        prompt += f"Input: {inp}\nOutput: {out}\n\n"
    prompt += f"Input: {new_input}\nOutput:"
    return prompt


def role_system(role_description: str, user_message: str) -> dict:
    """
    Returns a dict with 'system' and 'prompt' keys — pass system= to send_message().
    role_description: who/how the model should behave (e.g. "You are a terse senior security analyst.")
    """
    return {"system": role_description, "prompt": user_message}


def chain_of_thought(question: str) -> str:
    """Explicitly asks the model to reason step-by-step before answering."""
    return f"{question}\n\nThink through this step by step, then give your final answer on the last line."


def constrained_output(question: str, allowed_format: str) -> str:
    """
    allowed_format: a strict description of the exact output shape required.
    e.g. "Respond with exactly one word: 'positive', 'negative', or 'neutral'. No punctuation, no explanation."
    """
    return f"{question}\n\nOutput format requirement: {allowed_format}"


# Quick demo when run directly
if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from api_wrapper import GeminiWrapper

    wrapper = GeminiWrapper()

    print("=== ZERO-SHOT ===")
    print(wrapper.send_message(zero_shot("What is the capital of Japan?")))

    print("\n=== FEW-SHOT ===")
    examples = [("happy", "positive"), ("terrible", "negative")]
    print(wrapper.send_message(few_shot(examples, "mediocre")))

    print("\n=== ROLE/SYSTEM ===")
    rs = role_system("You are a terse senior security analyst. Answer in one sentence, no fluff.",
                      "What is a buffer overflow?")
    print(wrapper.send_message(rs["prompt"], system=rs["system"]))

    print("\n=== CHAIN-OF-THOUGHT ===")
    print(wrapper.send_message(chain_of_thought("If a train travels 60 miles in 1.5 hours, what is its average speed?")))

    print("\n=== CONSTRAINED OUTPUT ===")
    print(wrapper.send_message(constrained_output(
        "How do you feel about Mondays?",
        "Respond with exactly one word: 'positive', 'negative', or 'neutral'."
    )))