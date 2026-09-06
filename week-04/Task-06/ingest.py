import os
import re
from pypdf import PdfReader

DOCS_FOLDER = "docs"
CHUNK_SIZE = 800       # characters per chunk
CHUNK_OVERLAP = 150    # characters shared between consecutive chunks


def load_text_from_file(filepath):
    """Read a .txt or .pdf file and return its raw text."""
    if filepath.endswith(".pdf"):
        reader = PdfReader(filepath)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


def clean_text(text):
    """Collapse excess whitespace/newlines from messy PDF extraction."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """
    Split text into overlapping chunks.
    Overlap matters: without it, a sentence split exactly at a chunk boundary
    loses context on both sides, hurting retrieval quality.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap  # move forward, but re-include the overlap
    return chunks


def ingest_all():
    all_chunks = []  # list of dicts: {text, source, chunk_id}
    for filename in os.listdir(DOCS_FOLDER):
        filepath = os.path.join(DOCS_FOLDER, filename)
        if not os.path.isfile(filepath):
            continue

        raw = load_text_from_file(filepath)
        cleaned = clean_text(raw)
        chunks = chunk_text(cleaned)

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "source": filename,
                "chunk_id": f"{filename}::chunk_{i}"
            })
        print(f"{filename}: {len(chunks)} chunks")

    print(f"\nTotal chunks across all documents: {len(all_chunks)}")
    return all_chunks

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    # Collapse "V A U L T X" style letter-spacing back into "VAULTX"
    text = re.sub(r'\b(?:[A-Z] ){2,}[A-Z]\b', lambda m: m.group(0).replace(" ", ""), text)
    return text.strip()


if __name__ == "__main__":
    chunks = ingest_all()
    # Save a preview so you can inspect chunking quality
    with open("chunks_preview.txt", "w", encoding="utf-8") as f:
        for c in chunks[:5]:
            f.write(f"--- {c['chunk_id']} ---\n{c['text']}\n\n")
           