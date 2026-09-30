"""The two chunking strategies compared in this project.

structural : splitting on the PDF's own headings (font size). Every line whose font
             is bigger than the body starts a new chunk; everything under that heading
             -- paragraphs AND tables, across pages -- stays in one chunk.
recursive  : the standard convenience default. Try the biggest separator first
             (blank line, newline, end of sentence, space) and only cut by size when
             nothing else fits, so every piece stays under `size` characters.
"""
HEADING_EXTRA_PT = 2.0      # a heading is at least this many points bigger than body text
RECURSIVE_SIZE = 600        # max characters in one recursive piece


def split_structural(blocks, heading_extra_pt=HEADING_EXTRA_PT):
    """Chunk by the document's real headings. Returns chunks with their pages and lines."""
    body_size = sorted(b["size"] for b in blocks)[len(blocks) // 2]  # median font size
    chunks = []
    current = None
    for b in blocks:
        if b["size"] >= body_size + heading_extra_pt:      # a new section starts here
            current = {"title": b["text"], "lines": [b["text"]], "pages": {b["page"]}}
            chunks.append(current)
        else:
            if current is None:                             # content before the first heading
                current = {"title": "(front matter)", "lines": [], "pages": set()}
                chunks.append(current)
            current["lines"].append(b["text"])              # keep one line per source line
            current["pages"].add(b["page"])
    for c in chunks:
        c["text"] = " ".join(c["lines"])                    # flattened text for fact matching
        c["pages"] = sorted(c["pages"])
    return chunks


def split_recursive(text, size=RECURSIVE_SIZE):
    """Standard recursive splitter over a plain-text version of the same PDF."""
    separators = ["\n\n", "\n", ". ", " "]      # largest natural boundary first
    pieces = []

    def cut(part):
        part = part.strip()
        if not part:
            return
        if len(part) <= size:
            pieces.append(part)
            return
        for sep in separators:
            pos = part.rfind(sep, 0, size + 1)
            if pos > 0:
                cut(part[:pos])
                cut(part[pos + len(sep):])
                return
        cut(part[:size])                          # nothing else fits -- hard cut
        cut(part[size:])

    cut(text)
    return [{"title": f"recursive-{i}", "text": p, "pages": []} for i, p in enumerate(pieces)]