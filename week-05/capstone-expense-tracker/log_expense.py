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


def log_to_sheet(receipt_data, source="unknown"):
    payload = receipt_data.model_dump() if hasattr(receipt_data, "model_dump") else receipt_data
    payload["source"] = source

    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        print("Logged to Expense Log sheet successfully.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to log expense: {e}")
        return False