# Runbook: Expense Tracking Automation

## What it does
Extracts structured data from receipts (photo or text) using Gemini, applies a
confidence-based human-in-the-loop check, and logs results to Google Sheets via
an n8n automation — with retry, idempotency, and failure logging built in.

## How to trigger it
- Web app: visit the Render URL, use camera/upload/text input
- CLI: `python run_expense_tracker.py` (local desktop use)

## Where things live
- Code: GitHub repo, `week-05/capstone-expense-tracker/`
- Hosting: Render (web app), n8n Cloud (storage automation)
- Data: Google Sheets ("Expense Log")

## How to fix it if it breaks
1. Check Render's deploy logs for the web app
2. Check n8n Cloud's Executions tab for the automation
3. Check the `Errors` tab in the Google Sheet for logged failures
4. Common failure: Gemini API key expired/rate-limited — check `.env` / Render environment variables
5. Common failure: n8n webhook URL changed — update `N8N_WEBHOOK_URL` in `log_expense.py`

## Costs
See `roi_analysis.md` — near-zero marginal cost per run on current free-tier usage.