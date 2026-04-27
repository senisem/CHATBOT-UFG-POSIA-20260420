import os

import fitz
import pytest

from app.rag_utils import (
    PDF_PATH,
    extract_text_from_pdf,
    split_text_into_chunks,
    find_relevant_chunks,
    get_context_for_question,
)


def test_extract_text_from_pdf_reads_text_from_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Teste de extração de PDF")
    doc.save(str(pdf_path))
    doc.close()

    text = extract_text_from_pdf(str(pdf_path))

    assert "Teste de extração de PDF" in text


def test_split_text_into_chunks_respects_size_and_overlap():
    text = " ".join(str(i) for i in range(1, 51))
    chunks = split_text_into_chunks(text, chunk_size=10, overlap=2)

    assert len(chunks) == 7
    assert chunks[0].split()[0] == "1"
    assert chunks[1].split()[0] == "9"
    assert chunks[1].split()[:2] == ["9", "10"]


def test_find_relevant_chunks_returns_top_matches():
    chunks = ["cvm resolucao teste", "outro texto irrelevante", "legislacao cvm" ]
    relevant = find_relevant_chunks("legislacao cvm", chunks, top_k=2)

    assert len(relevant) == 2
    assert relevant[0] == "legislacao cvm"
    assert "cvm" in relevant[1]


def test_get_context_for_question_returns_empty_when_no_match(monkeypatch):
    monkeypatch.setattr("app.rag_utils.extract_text_from_pdf", lambda pdf_path: "uma amostra de texto sem correspondencia")

    context = get_context_for_question("pergunta irrelevante")

    assert context == ""


def test_get_context_for_question_returns_context_when_match(monkeypatch):
    monkeypatch.setattr("app.rag_utils.extract_text_from_pdf", lambda pdf_path: "cvm resolucao artigo 1 letra A")

    context = get_context_for_question("resolucao")

    assert "cvm" in context.lower()
    assert "resolucao" in context.lower()


def test_get_context_for_question_uses_default_pdf_path(monkeypatch):
    monkeypatch.setattr("app.rag_utils.extract_text_from_pdf", lambda pdf_path: "conteudo de teste")
    context = get_context_for_question("teste")
    assert context == "conteudo de teste"
