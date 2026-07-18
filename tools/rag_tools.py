"""
P3 owns this file — RAG Engineer.

Handles PDF -> text -> chunks -> embeddings -> ChromaDB -> retrieval.
Page numbers are tracked from extraction through to the final answer
so we can cite sources, not just generate free-floating text.
"""
import os
import chromadb
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from google import genai
from google.genai import types

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 4
EMBEDDING_MODEL = "gemini-embedding-001"
GEN_MODEL = "gemini-flash-latest"

_chroma_client = chromadb.PersistentClient(path="chroma_db")


def _get_collection(doc_id: str):
    return _chroma_client.get_or_create_collection(name=f"doc_{doc_id}")


def extract_and_chunk(pdf_path: str) -> list[dict]:
    """
    Extracts text page-by-page and splits into overlapping chunks.
    Page numbers are kept on every chunk so retrieval can cite sources.
    Returns a list of dicts: {text, page_number, chunk_index}.
    """
    reader = PdfReader(pdf_path)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    idx = 0
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if not text.strip():
            continue
        for piece in splitter.split_text(text):
            chunks.append({"text": piece, "page_number": page_num, "chunk_index": idx})
            idx += 1

    return chunks


def embed_and_store(chunks: list[dict], doc_id: str, api_key: str):
    """
    Embeds each chunk with Gemini's embedding model and stores it in
    a ChromaDB collection scoped to doc_id, so multiple documents
    don't bleed into each other's retrieval results.
    """
    client = genai.Client(api_key=api_key)
    collection = _get_collection(doc_id)

    texts = [c["text"] for c in chunks]
    ids = [f"{doc_id}_{c['chunk_index']}" for c in chunks]
    metadatas = [{"page_number": c["page_number"]} for c in chunks]

    # Batch in a simple loop — fine for capstone-scale documents.
    embeddings = []
    for text in texts:
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
        )
        embeddings.append(result.embeddings[0].values)

    collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
    return {"doc_id": doc_id, "chunks_stored": len(chunks)}


def retrieve(query: str, doc_id: str, api_key: str, k: int = TOP_K) -> list[dict]:
    """
    Embeds the query and retrieves the top-k most similar chunks from
    the given document's ChromaDB collection.
    """
    client = genai.Client(api_key=api_key)
    collection = _get_collection(doc_id)

    query_embedding = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    ).embeddings[0].values

    results = collection.query(query_embeddings=[query_embedding], n_results=k)

    retrieved = []
    for text, meta in zip(results["documents"][0], results["metadatas"][0]):
        retrieved.append({"text": text, "page_number": meta["page_number"]})
    return retrieved


def rag_query(query: str, doc_id: str, api_key: str) -> str:
    """
    Full RAG pipeline for a single question: retrieve relevant chunks,
    then ask Gemini to answer using ONLY those chunks, and cite page
    numbers. This is the single function P2 wraps as an agent tool.
    Use this when the user asks a question about an uploaded PDF/document.
    """
    client = genai.Client(api_key=api_key)
    chunks = retrieve(query, doc_id, api_key)

    if not chunks:
        return "No relevant content found in the document for this question."

    context = "\n\n".join(f"[Page {c['page_number']}]: {c['text']}" for c in chunks)
    prompt = (
        "Answer the question using ONLY the context below. If the answer "
        "isn't in the context, say so — do not make anything up. "
        "Cite the page number(s) your answer comes from.\n\n"
        f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
    )

    response = client.models.generate_content(model=GEN_MODEL, contents=prompt)
    return response.text
