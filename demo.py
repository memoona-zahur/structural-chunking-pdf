#!/usr/bin/env python3
"""Structural vs Recursive — a step-by-step walkthrough, not a one-liner.

    python3 demo.py            # runs all steps, one after another
    python3 demo.py --pause    # waits for Enter between steps (live demo)

Same engine as before (real PDF, exact facts, CPU embeddings), but printed as
a guided tour so you can follow WHAT each step does and WHY structural
chunking wins on this document.
"""
from __future__ import annotations

import sys

from sentence_transformers import SentenceTransformer

import chunkers
from extract_pdf import extract_pdf
from questions import QUESTIONS

PAUSE = "--pause" in sys.argv
TOP_K = 2
OUTPUT = "evidence.md"

# ---- tiny color helpers (auto-off when output is not a terminal) ----------
_COLOR = sys.stdout.isatty()


def _c(code: str, s: str) -> str:
    return f"\033[{code}m{s}\033[0m" if _COLOR else s


def green(s):  return _c("32", s)
def red(s):    return _c("31", s)
def yellow(s): return _c("33", s)
def bold(s):   return _c("1", s)
def dim(s):    return _c("2", s)

PASS, PART = green("PASS"), yellow("PARTIAL")
FAIL = red("FAIL")

# ---- helpers ---------------------------------------------------------------
def step(title: str):
    print("\n" + "=" * 72)
    print(bold(f"STEP: {title}"))
    print("=" * 72, flush=True)
    if PAUSE:
        input("  (press Enter to continue)")


def norm(text: str) -> str:
    return " ".join(text.split()).lower()


def fact_in_chunk(fact: str, text: str) -> bool:
    return norm(fact) in norm(text)


def show_chunks(chunks, method: str, n: int = 3):
    print(f"  {len(chunks)} chunks, avg {sum(len(c['text']) for c in chunks)//len(chunks)} chars")
    for c in chunks[:n]:
        print(f"    - {bold(c['title'])}   pages {c.get('pages')}")
    if len(chunks) > n:
        print(f"    ... and {len(chunks) - n} more")


def window_around(chunks, needle: str, width: int = 160) -> str:
    """Return a short quote from whichever chunk contains the needle."""
    for c in chunks:
        pos = norm(c["text"]).find(norm(needle))
        if pos >= 0:
            return c["text"][max(0, pos - 10):pos + width]
    return "(needle not found)"


def run_retrieval(method, chunks, model, index="chunks"):
    """Same retrieval as a production system: embed, take top-2, check the facts."""
    if index == "lines":
        units = [(i, ln) for i, c in enumerate(chunks) for ln in c.get("lines", [c["text"]]) if ln.strip()]
    else:
        units = [(i, c["text"]) for i, c in enumerate(chunks)]
    vec = model.encode([u[1] for u in units], normalize_embeddings=True)

    rows = []
    for q in QUESTIONS:
        qv = model.encode(q["question"], normalize_embeddings=True).reshape(1, -1)
        sims = (vec @ qv.T).ravel()
        top = sims.argsort()[::-1][:TOP_K]
        distinct = sorted({units[i][0] for i in top})
        retrieved = [chunks[i] for i in distinct]
        found = [any(fact_in_chunk(f, c["text"]) for c in retrieved) for f in q["facts"]]
        rows.append({
            "question": q["question"],
            "retrieved": [c["title"] for c in retrieved],
            "facts": q["facts"],
            "found": found,
        })
    return rows


# ---- the walkthrough -------------------------------------------------------
def main():
    print(bold("STRUCTURAL vs RECURSIVE chunking — real multi-page PDF"))
    print(dim("document: NASA Kepler Data Characteristics Handbook (47 pages)"))

    # ---------------- STEP 1: read the PDF -----------------------------
    step("1. Read the PDF into text lines (keeping page + font size)")
    blocks = extract_pdf()
    print(f"  indexed the main body: {blocks[0]['page']}-{blocks[-1]['page']} of 47 pages "
          f"(front matter skipped)")
    sizes = sorted(b["size"] for b in blocks)
    print(f"  {len(blocks)} text lines extracted, median font size "
          f"{sizes[len(sizes)//2]:.1f}pt")
    print(f"  sample line: \"{blocks[20]['text'][:70]}\"")

    # ---------------- STEP 2: find the headings ------------------------
    step("2. Headings are the lines whose font is ~2pt bigger than the body")
    body = sizes[len(sizes) // 2]
    heads = [b for b in blocks if b["size"] >= body + chunkers.HEADING_EXTRA_PT]
    print(f"  found {len(heads)} headings, e.g.:")
    for h in heads[1:8]:
        print(f"    - p{h['page']}  {h['text'][:60]}")

    # ---------------- STEP 3: chunk structurally ------------------------
    step("3. Structural chunking = one chunk per heading (section + its tables)")
    structural = chunkers.split_structural(blocks)
    print("  method:", bold("split_structural"))
    show_chunks(structural, "structural")

    # ---------------- STEP 4: chunk recursively -------------------------
    step("4. Recursive chunking = size-first, cut at the biggest natural boundary")
    doc_text = "\n".join(b["text"] for b in blocks)
    recursive = chunkers.split_recursive(doc_text)
    print("  method:", bold("split_recursive"))
    show_chunks(recursive, "recursive")

    # ---------------- STEP 5: the questions -----------------------------
    step("5. The exam: 6 questions, each needs 2 facts taken VERBATIM from the PDF")
    for i, q in enumerate(QUESTIONS, 1):
        print(f"  Q{i}. {q['question']}")
        for f in q["facts"]:
            print(f"      fact: ...\"{f}\"...")

    # ---------------- STEP 6: the crux, one concrete case ---------------
    step("6. Why it matters: the Safe-mode row in Table 7 spans two PDF pages")
    needle1 = "SAFE_MODE from 3553 to 3652"
    needle2 = "first valid LC back at science attitude"
    print("  structural: the whole row is ONE chunk:")
    print(f"    {green('BOTH facts')} in \"{bold('5.13 Anomaly Summary Table')}\" "
          f"pages {next(c['pages'] for c in structural if fact_in_chunk(needle1, c['text']))}")
    print(f"      \"{window_around(structural, needle1)}...\"")
    print("  recursive: cuts the very same row in the middle:")
    i1 = next(i for i, c in enumerate(recursive) if fact_in_chunk(needle1, c["text"]))
    i2 = next(i for i, c in enumerate(recursive) if fact_in_chunk(needle2, c["text"]))
    print(f"    fact 1 in {yellow('recursive-' + str(i1))}, fact 2 in "
          f"{yellow('recursive-' + str(i2))} -> different chunks, "
          f"only 1 can be retrieved")

    # ---------------- STEP 7: run retrieval for both methods ------------
    step("7. Embed every chunk once (CPU), retrieve top-2 for each question")
    print("  embedding ...", flush=True)
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    model.max_seq_length = 512
    rows_by = {
        "structural": run_retrieval("structural", structural, model, index="lines"),
        "recursive": run_retrieval("recursive", recursive, model, index="chunks"),
    }
    for method, rows in rows_by.items():
        print(f"\n  {bold(method)}:")
        for i, r in enumerate(rows, 1):
            mark = PASS if all(r["found"]) else FAIL
            print(f"    Q{i}. facts {sum(r['found'])}/{len(r['facts'])} [{mark}]  "
                  f"retrieved: {', '.join(r['retrieved'])}")

    # ---------------- STEP 8: the numbers -------------------------------
    step("8. Final scoreboard (hits / P@2 / R@2)")
    output = ["# Structural vs Recursive — on a real multi-page PDF",
              f"\nmethods: {list(rows_by)} | top-{TOP_K} | questions: {len(QUESTIONS)}",
              "\n| method | chunks | avg chunk chars | hits | P@2 | R@2 |",
              "|---|---|---|---|---|---|"]
    for method, chunks, index in (("structural", structural, "lines"), ("recursive", recursive, "chunks")):
        rows = rows_by[method]
        hits = sum(all(r["found"]) for r in rows)
        p = sum(sum(r["found"]) for r in rows) / (TOP_K * len(rows))
        r_ = sum(sum(r["found"]) for r in rows) / (2 * len(rows))
        avg = sum(len(c["text"]) for c in chunks) // len(chunks)
        n = f"{hits}/{len(rows)}"
        print(f"  {bold(method):<11} {len(chunks):>5} chunks  {avg:>4} chars  "
              f"hits {green(n) if hits == len(rows) else n:<4} P@2 {p:.2f}  R@2 {r_:.2f}")
        output.append(f"| {method} | {len(chunks)} | {avg} | {n} | {p:.3f} | {r_:.3f} |")
    output.append("\nper-question detail:")
    for method, rows in rows_by.items():
        output.append(f"\n## {method}")
        for i, r in enumerate(rows, 1):
            output.append(f"- Q{i}: {r['question']}")
            output.append(f"  facts found: {sum(r['found'])}/2 · hit: {all(r['found'])}")
            output.append(f"  retrieved: {r['retrieved']}")
    with open(OUTPUT, "w") as f:
        f.write("\n".join(output) + "\n")
    print(f"\n  full per-question transcript written to {bold(OUTPUT)}")
    print(dim("ever since: numbers re-run every time, nothing is hand-written"))


if __name__ == "__main__":
    main()