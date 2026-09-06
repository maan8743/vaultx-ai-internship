# Guardrails Writeup — Week 04 Task 06

## 1. "No answer found" handling

The system prompt explicitly instructs the model: "If the answer is not contained
in the context, respond exactly with: 'I don't know based on the provided
documents.'" This was tested extensively in Task 04's evaluation — 5 deliberately
unanswerable questions (capital of France, SANS statistics not present in
retrieved chunks, etc.) all correctly triggered this exact refusal, with zero
false answers.

Refusing beats guessing: an incorrect confident answer is far more dangerous
in a security/compliance context than an honest "I don't know," since a wrong
answer could be acted on without verification.

## 2. Hallucination check

A second, independent Gemini call reviews the main answer against the same
retrieved context, checking whether every claim in the answer is actually
supported by that context. This catches a specific failure mode: the main
answer call could technically retrieve correct sources but still add a plausible-
sounding detail that isn't really there. If the check flags the answer as
"UNGROUNDED," a warning banner is prepended to the response rather than hiding
the issue.

This is a real, separate LLM call — not just re-checking the same generation —
because a single model call reviewing its own work is less reliable than an
independent second pass with a narrower, more suspicious framing of the task.

## 3. Sources always shown

Every response — answerable or refused — returns the retrieved source chunks
and their similarity distances. This lets a human verify the answer's origin
directly, rather than trusting the AI's citation claims blindly. This was
true from Task 03 onward and confirmed at 100% groundedness across all 20
evaluation questions in Task 04.

## Summary

The system is designed to fail safely: refuse rather than guess, flag rather
than silently trust its own output, and always expose its sources so a human
retains final judgment.