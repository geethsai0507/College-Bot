import argparse
import os
import shutil
import re
import pandas as pd
import logging

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_community.vectorstores import FAISS

from get_embedding_function_copy import get_embedding_function
from config import DATA_PATH, CSV_PATH, FAISS_DIR, PDF_CHUNK_SIZE, PDF_CHUNK_OVERLAP, LOGS_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(LOGS_DIR, 'populate_database.log'),
    filemode='w'
)

def clear_database():
    if os.path.exists(FAISS_DIR):
        shutil.rmtree(FAISS_DIR)
        logging.info("✨ Cleared FAISS index directory.")


def load_and_chunk_pdfs() -> list[Document]:
    loader = PyPDFDirectoryLoader(DATA_PATH)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=PDF_CHUNK_SIZE,
        chunk_overlap=PDF_CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = splitter.split_documents(docs)
    return assign_pdf_chunk_ids(chunks)


def assign_pdf_chunk_ids(chunks: list[Document]) -> list[Document]:
    last_pid = None
    idx = 0
    for chunk in chunks:
        src = chunk.metadata.get("source", "")
        page = chunk.metadata.get("page", 0)
        pid = f"{src}:{page}"

        if pid == last_pid:
            idx += 1
        else:
            idx = 0

        chunk.metadata["id"] = f"{pid}:{idx}"
        last_pid = pid
    return chunks


def load_csv_documents() -> list[Document]:
    df = pd.read_csv(CSV_PATH)
    docs = []
    for i, row in df.iterrows():
        parts = []
        for col, val in row.items():
            if pd.notna(val):
                clean = str(val).strip().lower()
                parts.append(f"{col}: {clean}")

        # Optional: name normalization
        if "name" in row and pd.notna(row["name"]):
            parts.extend(normalize_name(row["name"]))

        text = "\n".join(parts)
        docs.append(
            Document(
                page_content=text,
                metadata={"id": f"csv_row_{i}", "source": "faculty_data.csv"},
            )
        )
    return docs


def normalize_name(name: str) -> list[str]:
    name_field = str(name).strip()
    no_hon = re.sub(r"(?i)\b(mr|ms|mrs|dr)\.\s*", "", name_field).strip()
    normalized_parts = [f"name_normalized: {no_hon.lower()}"]
    for p in re.split(r"\s+|\.", no_hon):
        if len(p) > 1:
            normalized_parts.append(f"name_part: {p.lower()}")
    return normalized_parts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the FAISS database.")
    args = parser.parse_args()

    if args.reset:
        clear_database()

    embed_fn = get_embedding_function()

    # 1) Load & chunk PDFs
    pdf_chunks = load_and_chunk_pdfs()
    logging.info(f"📄 PDF chunks prepared: {len(pdf_chunks)}")

    # 2) Initialize FAISS from PDFs (or load existing)
    if os.path.isdir(FAISS_DIR):
        logging.info("📂 Loading existing FAISS index…")
        db = FAISS.load_local(FAISS_DIR, embeddings=embed_fn, allow_dangerous_deserialization=True)
    else:
        logging.info("📂 Building new FAISS index from PDFs…")
        db = FAISS.from_documents(pdf_chunks, embedding=embed_fn)
        db.save_local(FAISS_DIR)
        logging.info(f"✅ Saved FAISS index with {len(pdf_chunks)} PDF chunks.")

    # 3) Load CSV docs and add only new ones
    csv_docs = load_csv_documents()
    existing_ids = set(db.docstore._dict.keys())
    new_docs = [d for d in csv_docs if d.metadata["id"] not in existing_ids]

    if new_docs:
        logging.info(f"📋 Adding {len(new_docs)} new CSV rows…")
        db.add_documents(new_docs, ids=[d.metadata["id"] for d in new_docs])
        db.save_local(FAISS_DIR)
        logging.info("✅ Successfully indexed CSV data.")
    else:
        logging.info("✅ No new CSV rows to add.")


if __name__ == "__main__":
    main()
