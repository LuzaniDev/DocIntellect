#!/usr/bin/env python3
"""Teste da API via HTTP com httpx (independente do PowerShell)."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx

API_URL = "http://127.0.0.1:8000"


def test_health():
    r = httpx.get(f"{API_URL}/health")
    assert r.status_code == 200, f"health falhou: {r.status_code}"
    assert r.json() == {"status": "ok"}
    print(f"  [HEALTH] {r.status_code} - OK")


def test_upload_image() -> str:
    image_path = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "nf_teste.png"
    if not image_path.exists():
        print("  Gerando imagem de teste...")
        from scripts.test_with_ocr import generate_invoice_image
        generate_invoice_image()

    with open(image_path, "rb") as f:
        r = httpx.post(f"{API_URL}/api/v1/documents/upload", files={"file": ("nf_teste.png", f, "image/png")})

    assert r.status_code == 201, f"upload falhou: {r.status_code} - {r.text}"
    data = r.json()
    doc_id = data["id"]
    print(f"  [UPLOAD] {r.status_code} - ID: {doc_id}")
    print(f"    filename: {data['filename']}")
    print(f"    status: {data['status']}")
    print(f"    size: {data['file_size']} bytes")
    return doc_id


def test_upload_pdf() -> str:
    pdf_path = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "nf_teste.pdf"
    if not pdf_path.exists():
        print("  PDF de teste nao encontrado. Execute scripts/test_pdf.py primeiro.")
        return ""

    with open(pdf_path, "rb") as f:
        r = httpx.post(f"{API_URL}/api/v1/documents/upload", files={"file": ("nf_teste.pdf", f, "application/pdf")})

    assert r.status_code == 201, f"upload PDF falhou: {r.status_code} - {r.text}"
    data = r.json()
    doc_id = data["id"]
    print(f"  [UPLOAD PDF] {r.status_code} - ID: {doc_id}")
    print(f"    filename: {data['filename']}")
    print(f"    status: {data['status']}")
    print(f"    size: {data['file_size']} bytes")
    return doc_id


def test_process(doc_id: str):
    r = httpx.post(f"{API_URL}/api/v1/documents/process/{doc_id}")
    assert r.status_code == 200, f"process falhou: {r.status_code} - {r.text}"
    data = r.json()
    print(f"  [PROCESS] {r.status_code}")
    print(f"    document_type: {data['document_type']}")
    print(f"    classification_confidence: {data['classification_confidence']:.2f}")
    print(f"    overall_confidence: {data['overall_confidence']:.2f}")
    print(f"    needs_review: {data['needs_review']}")
    print(f"    fields ({len(data['fields'])}):")
    for f in data["fields"]:
        print(f"      - {f['field_name']}: {f['field_value']} (conf: {f['confidence']:.2f}, method: {f['extraction_method']})")
    print(f"    raw_text (primeiros 100 chars): {data['raw_text'][:100]!r}...")
    return data


def main():
    print("=" * 50)
    print(" TESTE DA API - DOCINTELLECT RPA")
    print("=" * 50)

    test_health()
    print("\n--- Teste com IMAGEM ---")
    doc_id = test_upload_image()
    test_process(doc_id)

    print("\n--- Teste com PDF ---")
    doc_id = test_upload_pdf()
    test_process(doc_id)

    print("\n" + "=" * 50)
    print(" TODOS OS TESTES PASSARAM!")
    print("=" * 50)


if __name__ == "__main__":
    main()
