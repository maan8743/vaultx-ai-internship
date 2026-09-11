import os
import socket
from flask import Flask, request, render_template, jsonify
from extract_receipt import extract_receipt_from_image
from log_expense import log_to_sheet
from query_expenses import answer_question

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "photo" not in request.files:
        return jsonify({"error": "No photo provided"}), 400

    photo = request.files["photo"]
    save_path = os.path.join(UPLOAD_FOLDER, "latest_receipt.jpg")
    photo.save(save_path)

    try:
        result = extract_receipt_from_image(save_path)
    except Exception as e:
        return jsonify({"error": f"Extraction failed: {e}"}), 500

    logged = log_to_sheet(result, source="mobile_web")

    return jsonify({
        "extracted": result.model_dump(),
        "logged": logged,
    })


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        answer = answer_question(question)
    except Exception as e:
        return jsonify({"error": f"Query failed: {e}"}), 500

    return jsonify({"answer": answer})


def get_local_ip():
    """Find this machine's local network IP, so we can tell the user the URL
    to open on their phone or another device on the same WiFi."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    local_ip = get_local_ip()
    print("\n=== Expense Tracker Web App ===")
    print(f"On this computer:  http://localhost:{port}")
    print(f"On your phone / another device (same WiFi):  http://{local_ip}:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)