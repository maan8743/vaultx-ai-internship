from collections import defaultdict
from query_expenses import fetch_expenses

def generate_summary():
    expenses = fetch_expenses()

    by_category = defaultdict(float)
    total_spent = 0.0

    for row in expenses:
        try:
            amount = float(row.get("total", 0) or 0)
        except ValueError:
            continue
        category = row.get("category", "other")
        by_category[category] += amount
        total_spent += amount

    print("\n=== Spending Summary ===")
    print(f"Total spent: ${total_spent:.2f}\n")
    print("By category:")
    for category, amount in sorted(by_category.items(), key=lambda x: -x[1]):
        pct = (amount / total_spent * 100) if total_spent > 0 else 0
        print(f"  {category:15s} ${amount:8.2f}  ({pct:.1f}%)")

if __name__ == "__main__":
    generate_summary()