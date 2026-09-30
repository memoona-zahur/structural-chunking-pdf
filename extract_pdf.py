"""Read a real multi-page PDF into text blocks (line-by-line with page + font size).

The font size is what lets us spot headings later: body text in this manual is ~10pt
and the section headings are ~12-14pt.
"""
from pathlib import Path

import pdfplumber

PDF_PATH = Path("sample.pdf")
# Skip the front matter (title, signature, document-control and table-of-contents
# pages) and index the main body -- the same way a real RAG pipeline strips
# boilerplate pages before building the vector index.
START_PAGE = 8


def extract_pdf(pdf_path=PDF_PATH, start_page=START_PAGE, end_page=None):
    """Return a list of blocks: {"page": int, "text": str, "size": float}.

    Every line of the PDF becomes one block. Headings are NOT decided here --
    we just keep the font size so the chunker can decide.
    """
    blocks = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_no, page in enumerate(pdf.pages, start=1):
            if page_no < start_page:
                continue
            if end_page and page_no > end_page:
                break
            words = page.extract_words(extra_attrs=["size"])

            # group words that share the same vertical position into lines
            lines = {}
            for w in words:
                lines.setdefault(round(w["top"]), []).append(w)

            for top in sorted(lines):
                row = sorted(lines[top], key=lambda w: w["x0"])
                text = " ".join(w["text"] for w in row).strip()
                if not text:
                    continue

                # running page header/footer that repeats on every page -- drop it
                if text.startswith("KSCI-19040-001") or text.endswith("of 47"):
                    continue

                blocks.append({"page": page_no, "text": text, "size": max(w["size"] for w in row)})
    return blocks