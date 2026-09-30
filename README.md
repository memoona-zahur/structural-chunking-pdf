# Structural vs Recursive Chunking — a real-PDF comparison

A small, dependency-light demo that answers one question:

> On a real technical PDF (47 pages, many section headings and wide tables),
> does chunking **by the document's own headings** beat the **standard
> recursive** splitter?

## What we compare

| method        | what a chunk is                                  |
|---------------|--------------------------------------------------|
| `structural`  | one full section of the manual (its heading + all paragraphs and tables under it, kept together across pages) |
| `recursive`   | a ~600-character piece, cut at the biggest natural boundary (`\n\n`, `\n`, `. `, space) that fits |

Both are applied to the **same** document and judged with the **same** retrieval
test — no LLM calls and no manual grading anywhere.

## The test

`questions.py` holds 6 questions a real reader of the manual would ask. Every
question carries **2 required facts taken verbatim from the PDF**. A question
counts as answered only when **both** facts are found inside the chunks we
retrieve, and a fact counts as found only by an exact (whitespace-insensitive)
substring match — deterministic, no judgement involved.

For each method we:
1. embed every chunk once (CPU-only, `all-MiniLM-L6-v2`);
2. retrieve the most relevant sections for each question;
3. report `hits` (both facts found), `P@2` and `R@2`.

One honest technical note: structural sections can be long, and a whole section
is too big to vector-match directly (it gets diluted/truncated). So structural
uses the standard **small-to-big** trick that your PDF notes describe — the
*lines inside* a section are embedded to pick the relevant sections, but the
unit we return is always the **whole section**. The recursive method has no
sections to offer, so its unit is its own chunk.

## Result

| method      | chunks | avg chunk chars | hits | P@2 | R@2 |
|-------------|--------|-----------------|------|-----|-----|
| structural  | 93     | 813             | 6/6  | 1.0 | 1.0 |
| recursive   | 137    | 551             | 1/6  | 0.33| 0.33|

`evidence.md` records the per-question detail, so the numbers can be checked
and re-run.

## Why structural wins so clearly here

- Recursive cuts by *character budget*, so a wide table (cadence numbers, dates,
  Safe-mode rows that span two PDF pages) gets severed mid-row. Fact 1 lands in
  one piece, fact 2 in another — the retriever can only hand you one of them.
- Structural treats the document the way its author did: a section heading owns
  everything between it and the next heading, including **tables that span
  pages**. Retrieve the section, and you get both facts.

## Files

| file | why |
|------|-----|
| `sample.pdf` | the NASA Kepler Data Characteristics Handbook (KSCI-19040-001, public domain) |
| `extract_pdf.py` | reads the PDF into text lines, keeping page + font size (headings are bigger than body text) |
| `chunkers.py` | the two strategies: `split_structural` (font-size headings) and `split_recursive` |
| `questions.py` | the 6 questions + their verbatim required facts |
| `demo.py` | the step-by-step walkthrough (numbers are computed on every run, nothing hand-written) |
| `evidence.md` | last run's full per-question transcript |

## Run it (step by step, not one black box)

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python demo.py            # full walkthrough
.venv/bin/python demo.py --pause    # same, but waits for Enter between steps (live demo)
```

`demo.py` is a narrated tour, not a hidden pipeline. You watch it happen:

1. **Read the PDF** into text lines, keeping page + font size.
2. **Find the headings** — the lines whose font is ~2pt bigger than body text.
3. **Chunk structurally** — one chunk per heading (section + its tables together).
4. **Chunk recursively** — size-first, cut at the biggest natural boundary.
5. **Show the exam** — 6 questions, each with 2 facts taken verbatim from the PDF.
6. **The crux, one concrete case** — the Safe-mode row in Table 7 spans two PDF
   pages: structural keeps both facts in one chunk, recursive cuts the row in two.
7. **Run retrieval** for both methods (top-2) and watch the per-question PASS/FAIL.
8. **The scoreboard** (hits / P@2 / R@2) and a full transcript in `evidence.md`.

## Caveats (kept honest)

- Headings are detected by font size (`size >= median body size + 2pt`), which is
  a decent heuristic for this kinds of manuals but not a universal rule.
- The demo indexes the main body (Sections 1–9); the title/signature/control and
  the table-of-contents pages are skipped, exactly like a production pipeline
  strips boilerplate before building the index.
- Facts are hard-coded substrings of this specific document — fine for an honest
  A/B, but a general evaluation would need a labelled dataset.