import time
from rag_query import answer_question

# Built from REAL confirmed answers your RAG system already gave, based on
# NetSupport_RAT_Incident_Report.pdf and NIST.CSWP.29.pdf.
# Format: (question, expected_keyword_or_fact, should_be_answerable)
EVAL_SET = [
    # --- NetSupport RAT Incident Report — confirmed answerable ---
    ("What is the victim IP in the indicator assessment?", "10.11.26.183", True),
    ("What is the victim workstation hostname?", "DESKTOP-B8TQK49", True),
    ("What is the victim workstation MAC address?", "d0:57:7b:ce:fc:8b", True),
    ("What is the logged-in Windows account on the victim workstation?", "oboomwald", True),
    ("What suspicious domain did the workstation access?", "modandcrackedapk.com", True),
    ("What IP address does the suspicious domain resolve to?", "193.42.38.139", True),
    ("What is the RAT command and control IP and port?", "194.180.191.64", True),
    ("What URI is used by the RAT for command and control?", "/fakeurl.htm", True),
    ("What User-Agent string indicates NetSupport RAT activity?", "NetSupport Manager/1.3", True),
    ("What server header indicates NetSupport RAT infrastructure?", "NetSupport Gateway/1.8", True),
    ("What website is a potential infection-chain component in this incident?", "classicgrand.com", True),
    ("What can the PCAP evidence NOT prove about this incident?", "who operated the RAT", True),

    # --- NIST Cybersecurity Framework — confirmed answerable ---
    ("What does the IDENTIFY function in the NIST framework mean?", "current cybersecurity risks are understood", True),
("What does ID.RA-01 cover in the NIST framework?", ["vulnerabilities", "assets"], True),
    ("What does ID.RA-02 cover in the NIST framework?", "cyber threat intelligence", True),

    # --- Deliberately unanswerable (should trigger refusal) ---
    ("What is the capital of France?", None, False),
    ("What percentage of organizations reported phishing in the SANS report?", None, False),
    ("When was the NetSupport RAT incident detected and resolved?", None, False),
    ("What is the CEO of the affected company's name?", None, False),
    ("What programming language was used to build the RAT malware?", None, False),
]


def run_evaluation():
    correct = 0
    grounded = 0
    results = []

    for question, expected_keyword, should_answer in EVAL_SET:
        result = answer_question(question)
        answer = result["answer"]

        refused = "i don't know" in answer.lower()

        if should_answer:
            if isinstance(expected_keyword, list):
                is_correct = all(kw.lower() in answer.lower() for kw in expected_keyword) and not refused
            else:
                is_correct = (expected_keyword or "").lower() in answer.lower() and not refused
        else:
            is_correct = refused  # correct behavior here IS refusing

        is_grounded = len(result["sources"]) > 0

        correct += is_correct
        grounded += is_grounded
        results.append((question, answer, is_correct, refused))

        status = "PASS" if is_correct else "FAIL"
        print(f"\n[{status}] {question}")
        print(f"  Answer: {answer[:200]}")
        time.sleep(4)  # stay under free-tier rate limit

    accuracy = correct / len(EVAL_SET) * 100
    groundedness = grounded / len(EVAL_SET) * 100

    print(f"\n=== RESULTS ===")
    print(f"Accuracy: {accuracy:.1f}% ({correct}/{len(EVAL_SET)})")
    print(f"Groundedness (retrieved real sources): {groundedness:.1f}%")

    with open("evaluation_log.txt", "w", encoding="utf-8") as f:
        f.write(f"Accuracy: {accuracy:.1f}%\nGroundedness: {groundedness:.1f}%\n\n")
        for q, a, correct_flag, refused in results:
            status = "PASS" if correct_flag else "FAIL"
            f.write(f"[{status}] Q: {q}\nA: {a}\nRefused: {refused}\n\n")

    return accuracy, groundedness, results


if __name__ == "__main__":
    run_evaluation()