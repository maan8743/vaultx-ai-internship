from flask import Flask, request, jsonify
from rag_query import answer_question

app = Flask(__name__)


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "No question provided"}), 400

    result = answer_question(question)
    return jsonify(result)


if __name__ == "__main__":
    app.run(port=5000)