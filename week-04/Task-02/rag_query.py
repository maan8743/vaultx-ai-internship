import os
import chromadb
from dotenv import load_dotenv
from google import genai

load_dotenv()

PERSIST_DIR = "chroma_db"
COLLECTION_NAME = "vaultx_docs"
TOP_K = 4


def get_embedding(client, text):
    result = client.models.embed_content(model="gemini-embedding-001", contents=text)
    return result.embeddings[0].values


def retrieve(client, collection, question, top_k=TOP_K):
    query_embedding = get_embedding(client, question)
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "distance": results["distances"][0][i],
        })
    return chunks


def answer_question(question):
    gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = chroma_client.get_collection(COLLECTION_NAME)

    retrieved = retrieve(gemini_client, collection, question)

    # Build a context block that clearly separates each source chunk
    context = "\n\n".join(
        f"[Source {i+1}: {c['source']}]\n{c['text']}"
        for i, c in enumerate(retrieved)
    )

    prompt = f"""Answer the question using ONLY the context below. Do not use any
outside knowledge. Cite which source number(s) support your answer, like [Source 1].
If the answer is not contained in the context, respond exactly with:
"I don't know based on the provided documents."

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""

    response = gemini_client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )

    return {
        "answer": response.text,
        "sources": [{"source": c["source"], "distance": c["distance"]} for c in retrieved],
    }


if __name__ == "__main__":
    while True:
        question = input("\nAsk a question (or 'quit'): ")
        if question.lower() == "quit":
            break
        result = answer_question(question)
        print(f"\nANSWER:\n{result['answer']}")
        print(f"\nRETRIEVED FROM:")
        for s in result["sources"]:
            print(f"  - {s['source']} (distance: {s['distance']:.4f})")