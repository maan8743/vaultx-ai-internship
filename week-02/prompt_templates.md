# Prompt Pattern Library

## Zero-shot
Ask directly with no examples. Fast, works well for simple, well-known tasks.
Use when: the task is common enough the model already "knows" the expected format.

## Few-shot
Provide 2-3 input→output example pairs before the real question, so the model
infers the exact pattern/format you want.
Use when: you need a specific, non-obvious output style or format.

## Role/System
Set persona and behavior rules in a system message, separate from the user's question.
Use when: you want consistent tone/behavior across many different questions.

## Chain-of-thought
Ask the model to reason step-by-step before answering.
Use when: the task involves logic, math, or multi-step reasoning — improves accuracy
by giving the model "room to think" before committing to a final answer.

## Constrained output
Explicitly restrict the response format/length/vocabulary.
Use when: the output needs to be machine-parseable or fit a strict UI constraint.