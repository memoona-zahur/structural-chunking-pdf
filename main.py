#!/usr/bin/env python3
"""Compare STRUCTURAL vs RECURSIVE chunking on a real multi-page PDF.

The story:
  recursive chunking is the standard default, but on a heading-rich technical PDF
  that is full of wide tables, cutting by size tears facts apart. Structural
  chunking respects the document's own headings (section + its table together),
  so both required facts of a question usually land in the SAME chunk.

How we judge (no LLM key needed):
  - questions.py holds 6 questions, each with 2 required facts verbatim from the PDF;
  - every chunk is embedded once (all-MiniLM-L6-v2 on CPU);
  - for each question we retrieve the top-2 most similar chunks;
  - hit   = both facts found inside those 2 chunks,
    P@2  = retrieved chunks that contain at least one required fact / 2,
    R@2  = required facts found / 2,
    every fact is a substring check (deterministic).
"""
import json

import pdfplumber
from sentence_transformers import SentenceTransformer

import chunkers
from extract_pdf import extract_pdf
from questions import QUESTIONS

TOP_K = 2
OUTPUT = "evidence.md"


def norm(text: str) -> str:
    """Collapse all whitespace so that wrapped lines still match."""
    return " ".join(text.split()).lower()


def fact_in_chunk(fact: str, text: str) -> bool:
    return norm(fact) in norm(text)


def search(method, chunks, model, questions, index="chunks"):
    """Run the 6-question retrieval test for one method; return per-question scores.

    index="lines" = small-to-big: embed the lines INSIDE each section to decide which
    sections are relevant, then return the whole sections. Big sections are hard to
    vector-match directly (they get diluted/truncated), so this is how a real system
    would index them. The returned unit stays the WHOLE section -- that part never changes.
    """
    if index == "lines":
        units = [(i, ln) for i, c in enumerate(chunks) for ln in c.get("lines", [c["text"]]) if ln.strip()]
    else:
        units = [(i, c["text"]) for i, c in enumerate(chunks)]
    unit_texts = [u[1] for u in units]
    unit_vec = model.encode(unit_texts, normalize_embeddings=True)

    rows = []
    for q in questions:
        q_vec = model.encode(q["question"], normalize_embeddings=True).reshape(1, -1)
        sims = (unit_vec @ q_vec.T).ravel()
        top = sims.argsort()[::-1][:TOP_K]
        distinct = sorted({units[i][0] for i in top})          # distinct sections, in order
        retrieved = [chunks[i] for i in distinct]
        found = [any(fact_in_chunk(f, c["text"]) for c in retrieved) for f in q["facts"]]
        rows.append({
            "question": q["question"],
            "retrieved": [c["title"] for c in retrieved],
            "facts_found": sum(found),
            "hit": all(found),
        })
    return rows


def summarize(method, chunks, rows):
    hits = sum(r["hit"] for r in rows)
    prec = sum(r["facts_found"] for r in rows) / (TOP_K * len(rows))
    recall = sum(r["facts_found"] for r in rows) / (2 * len(rows))
    avg_chars = sum(len(c["text"]) for c in chunks) // max(len(chunks), 1)
    return {
        "method": method,
        "chunks": len(chunks),
        "avg_chunk_chars": avg_chars,
        "hits": f"{hits}/{len(rows)}",
        "P@2": round(prec, 3),
        "R@2": round(recall, 3),
    }


def main():
    # 1. read the PDF (47 real pages) into lines
    blocks = extract_pdf()
    doc_text = "\n".join(b["text"] for b in blocks)

    # 2. chunk it once per strategy
    methods = {
        "structural": chunkers.split_structural(blocks),
        "recursive": chunkers.split_recursive(doc_text),
    }

    # 3. embed chunks once (CPU, ~1 minute the first time it downloads the model)
    print("embedding chunks ...", flush=True)
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    model.max_seq_length = 512

    # 4. run the test and print the comparison
    results = []
    all_rows = {}
    indexes = {"structural": "lines", "recursive": "chunks"}
    for method, chunks in methods.items():
        rows = search(method, chunks, model, QUESTIONS, index=indexes[method])
        all_rows[method] = rows
        results.append(summarize(method, chunks, rows))
        print(json.dumps(results[-1], indent=2))

    # 5. write an evidence file with the same numbers (like a saved transcript)
    lines = ["# Structural vs Recursive — on a real multi-page PDF",
             f"\nmethods: {list(methods)} | top-{TOP_K} | questions: {len(QUESTIONS)}",
             "\n| method | chunks | avg chunk chars | hits | P@2 | R@2 |",
             "|---|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['method']} | {r['chunks']} | {r['avg_chunk_chars']} | {r['hits']} | {r['P@2']} | {r['R@2']} |")
    lines.append("\nper-question detail:")
    for method, rows in all_rows.items():
        lines.append(f"\n## {method}")
        for r in rows:
            lines.append(f"- Q: {r['question']}")
            lines.append(f"  facts found: {r['facts_found']}/2 · hit: {r['hit']}")
            lines.append(f"  retrieved: {r['retrieved']}")
    with open(OUTPUT, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nwrote {OUTPUT}")


if __name__ == "__main__":
    main()