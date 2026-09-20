import requests

N8N_WEBHOOK_URL = "https://maan8743.app.n8n.cloud/webhook/log-expense"
def is_likely_duplicate(new_entry, existing_expenses):
    """Flags a probable duplicate: same merchant, same date, same total."""
    for row in existing_expenses:
        if (row.get("merchant", "").lower() == new_entry.get("merchant", "").lower()
                and row.get("date", "") == new_entry.get("date", "")
                and str(row.get("total", "")) == str(new_entry.get("total", ""))):
            return True
    return False


def log_to_sheet(receipt_data, source="unknown", max_retries=3):
    from query_expenses import fetch_expenses

    payload = receipt_data.model_dump() if hasattr(receipt_data, "model_dump") else receipt_data
    payload["source"] = source

    try:
        existing = fetch_expenses()
        if is_likely_duplicate(payload, existing):
            print("Duplicate detected — skipping (already logged).")
            return False
    except Exception as e:
        print(f"Could not check for duplicates: {e}. Proceeding anyway.")

    # ... existing retry logic continues here