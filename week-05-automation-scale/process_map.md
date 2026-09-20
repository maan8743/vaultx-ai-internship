# Process Map: Expense Tracking

## BEFORE (manual process)
1. Keep the physical receipt or forget to
2. At the end of the week/month, gather receipts
3. Manually type each one into a spreadsheet: merchant, date, amount, category
4. Manually decide the category for each line
5. Manually total up spending by category (or don't, and never actually know)
6. To answer "how much did I spend on X" — manually filter/sum the spreadsheet

**Time per receipt:** ~2-3 minutes of manual entry
**Reliability:** Receipts get lost, entry gets skipped when busy, categorization is inconsistent
**Typical outcome:** Most people abandon manual tracking within weeks

## AFTER (automated process)
1. Take a photo (phone or laptop camera) — or paste receipt text
2. AI extracts merchant, date, total, category, and line items automatically
3. Confidence check flags anything unclear for review instead of guessing
4. Automatically logged to Google Sheets via n8n — no manual typing
5. Ask a question in plain English anytime — instant, accurate answer computed from real data

**Time per receipt:** ~10-15 seconds (mostly just taking the photo)
**Reliability:** Consistent categorization, nothing silently lost, low-confidence entries flagged not fabricated
**Typical outcome:** Zero ongoing manual effort after setup