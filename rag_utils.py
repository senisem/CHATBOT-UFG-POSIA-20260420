"""
Utilitários para RAG (Retrieval-Augmented Generation) usando PDF.
Extrai contexto relevante do arquivo resol175consolid.pdf para enriquecer o prompt do chatbot.
"""

import os
from typing import List
import fitz  # PyMuPDF
import re

PDF_PATH = os.path.join(os.path.dirname(__file__), "resol175consolid.pdf")


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrai todo o texto do PDF.
    """
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text


def split_text_into_chunks(text: str, chunk_size: int = 1500, overlap: int = 200) -> List[str]:
    """
    Divide o texto em chunks para busca semântica.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


def find_relevant_chunks(question: str, chunks: List[str], top_k: int = 3) -> List[str]:
    """
    Busca os chunks mais relevantes para a pergunta usando similaridade simples (TF).
    """
    question_words = set(re.findall(r"\w+", question.lower()))
    scored = []
    for chunk in chunks:
        chunk_words = set(re.findall(r"\w+", chunk.lower()))
        score = len(question_words & chunk_words)
        scored.append((score, chunk))
    scored.sort(reverse=True)
    return [chunk for score, chunk in scored[:top_k] if score > 0]


def get_context_for_question(question: str, pdf_path: str = PDF_PATH) -> str:
    """
    Extrai contexto relevante do PDF para a pergunta.
    """
    text = extract_text_from_pdf(pdf_path)
    chunks = split_text_into_chunks(text)
    relevant_chunks = find_relevant_chunks(question, chunks)
    if not relevant_chunks:
        return ""
    return "\n---\n".join(relevant_chunks)
