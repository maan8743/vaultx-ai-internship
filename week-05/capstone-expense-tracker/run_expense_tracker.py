from capture_receipt import capture_photo
from extract_receipt import extract_receipt_from_image
from log_expense import log_to_sheet

if __name__ == "__main__":
    print("=== Expense Tracker ===\n")

    photo_path = capture_photo()
    print(f"\nExtracting data from {photo_path}...")

    result = extract_receipt_from_image(photo_path)
    print("\n" + result.model_dump_json(indent=2))

    if result.confidence == "low":
        print("\n⚠️  LOW CONFIDENCE — this extraction may be inaccurate.")
        confirm = input("Log it anyway? (y/n): ")
        if confirm.lower() != "y":
            print("Skipped — not logged.")
            exit()

    log_to_sheet(result, source="camera")
    print("\nDone — check your Expense Log sheet.")