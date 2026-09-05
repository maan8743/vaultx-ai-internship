Evaluation Set
RAG Evaluation Report - Week 04 Task 04

20 question-answer pairs built from real, verified facts across three documents: NetSupport_RAT_Incident_Report.pdf,
 NIST.CSWP.29.pdf, and SANS-2025-Security-Awareness-Report.pdf.

⚫ 15 questions with a known-correct answer confirmed to exist in the documents
⚫ 5 questions deliberately unanswerable from these documents, to test refusal behavior
Baseline Results (Run 1)
Accuracy: 95.0% (19/20)
Groundedness: 100.0% (20/20) - every question, answerable or not, retrieved real source chunks.

All 5 unanswerable questions correctly triggered the refusal response ("I don't know based on the provided
documents"), including questions targeting the SANS report specifically - the system correctly recognized when its retrieved context didn't contain relevant statistics, rather than guessing.
Failure Analysis
1 failure: "What does ID.RA-01 cover in the NIST framework?"
• Actual answer given: "ID.RA-01 covers the identification, validation, and recording of vulnerabilities in assets" this is factually correct and matches the real NIST wording.

• Root cause: the evaluation script itself, not the RAG system. The test checked for an exact substring match against one specific phrasing ("vulnerabilities in assets are identified"). The model expressed the same fact in a different word order, so the exact-match check failed even though the answer was correct.

⚫ This was not a retrieval problem, a chunking problem, or a hallucination—the answer was grounded and accurate. It was a brittleness in how correctness was measured.

Improvement Made

Changed the evaluation method from exact-phrase substring matching to multi-keyword matching: instead of requiring one exact phrase to appear verbatim, the check now verifies that all key terms (e.g., "vulnerabilities" and "assets") appear somewhere in the answer, regardless of word order or surrounding phrasing. This is a more realistic and fair way to grade an LLM's answer, since natural language allows many correct phrasings of the same fact.
Results After Improvement (Run 2)
Accuracy: 100.0% (20/20)
Groundedness: 100.0% (20/20)
The improvement did not change anything about the RAG system's actual retrieval or generation behavior - it corrected a flaw in the test itself, revealing that the system's real performance was already at 100% on this evaluation set; the original 95% was an artifact of an overly strict grader.
Other Observations
SANS report questions retrieved real chunks in every case (confirmed groundedness), but two different phrasings of statistics-related questions both correctly resulted in refusal, since the retrieved chunks did not contain a clear, directly-answerable statistic. This suggests either the specific statistics live in parts of the document with lower semantic similarity to these generic phrasings, or the report is structured (tables, charts) in a way that doesn't chunk cleanly into retrievable prose. Future improvement: investigate PDF table extraction, or test more specific questions naming an exact stat category.
