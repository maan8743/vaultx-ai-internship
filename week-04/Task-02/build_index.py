import os
import time
import chromadb
from dotenv import load_dotenv
from google import genai
from ingest import ingest_all

load_dotenv()

PERSIST_DIR = "chroma_db"
COLLECTION_NAME = "vaultx_docs"
MAX_RETRIES = 4


def get_embedding(client, text, max_retries=MAX_RETRIES):
    """Get an embedding with retry on transient network/API errors."""
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            result = client.models.embed_content(
                model="gemini-embedding-001",
                contents=text,
            )
            return result.embeddings[0].values
        except Exception as e:
            last_error = e
            wait = 2 ** attempt  # 2s, 4s, 8s, 16s
            print(f"    [Retry {attempt}/{max_retries}] {type(e).__name__}: {e}. Waiting {wait}s...")
            time.sleep(wait)
    raise RuntimeError(f"Embedding failed after {max_retries} attempts: {last_error}")


def build_index():
    gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

    chunks = ingest_all()

    # Resume support: skip any chunk_id that's already indexed from a previous run
    existing_ids = set(collection.get()["ids"]) if collection.count() > 0 else set()
    if existing_ids:
        print(f"Resuming — {len(existing_ids)} chunks already indexed, skipping those.")

    remaining = [c for c in chunks if c["chunk_id"] not in existing_ids]
    print(f"{len(remaining)} chunks left to index out of {len(chunks)} total.\n")

    for i, chunk in enumerate(remaining):
        try:
            embedding = get_embedding(gemini_client, chunk["text"])
            collection.add(
                ids=[chunk["chunk_id"]],
                embeddings=[embedding],
                documents=[chunk["text"]],
                metadatas=[{"source": chunk["source"]}],
            )
            print(f"Indexed {i+1}/{len(remaining)}: {chunk['chunk_id']}")
        except RuntimeError as e:
            print(f"\nGiving up on {chunk['chunk_id']} after retries: {e}")
            print("You can just re-run this script — it will resume from here.")
            raise

        time.sleep(1)  # small pause between calls to avoid rate limits

    print(f"\nIndex built and persisted to ./{PERSIST_DIR}")
    print(f"Total vectors in collection: {collection.count()}")


if __name__ == "__main__":
    build_index()