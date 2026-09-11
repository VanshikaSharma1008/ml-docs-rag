import json
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
CHUNK_FILE = Path(__file__).resolve().parent.parent / "data" / "chunks.json"

MAX_CHARS = 1500
MIN_CHARS = 200


def split_sections(text):
    """Split on ## headings. Returns (page_title, [(section_title, body)])."""
    lines = text.split("\n")

    page_title = ""
    if lines and lines[0].startswith("# "):
        page_title = lines[0][2:].strip()
        lines = lines[1:]

    sections = []
    current_title = "Introduction"
    current_lines = []
    in_code = False

    for line in lines:
        if line.startswith("```"):
            in_code = not in_code

        if not in_code and line.startswith("## "):
            if current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))

    return page_title, [(t, b) for t, b in sections if b]


def split_long(body):
    """Split an oversized section line by line, keeping code fences intact."""
    if len(body) <= MAX_CHARS:
        return [body]

    # Pass 1: group lines into units.
    # A fenced code block is ONE unit. Every other line is its own unit.
    units = []
    buffer = []
    in_code = False

    for line in body.split("\n"):
        if line.startswith("```"):
            buffer.append(line)
            if in_code:
                units.append("\n".join(buffer))
                buffer = []
            in_code = not in_code
            continue

        if in_code:
            buffer.append(line)
        else:
            units.append(line)

    if buffer:
        units.append("\n".join(buffer))

    # Pass 2: greedily pack units into chunks under MAX_CHARS
    parts = []
    current = []
    size = 0

    for unit in units:
        if size + len(unit) > MAX_CHARS and current:
            parts.append("\n".join(current))
            current = []
            size = 0

        current.append(unit)
        size += len(unit) + 1

    if current:
        parts.append("\n".join(current))

    # Merge a small trailing part back into the previous one
    if len(parts) > 1 and len(parts[-1]) < MIN_CHARS:
        parts[-2] = parts[-2] + "\n" + parts[-1]
        parts.pop()

    return parts


def chunk_document(record):
    page_title, sections = split_sections(record["text"])
    chunks = []

    for section_title, body in sections:
        for i, part in enumerate(split_long(body)):
            header = f"{page_title} > {section_title}" if section_title else page_title
            chunks.append({
                "text": f"{header}\n\n{part}",
                "url": record["url"],
                "tool": record["tool"],
                "source_type": record["source_type"],
                "page_title": page_title,
                "section": section_title,
                "part": i,
            })

    return chunks


def main():
    all_chunks = []

    for path in sorted(RAW_DIR.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        all_chunks.extend(chunk_document(record))

    CHUNK_FILE.write_text(
        json.dumps(all_chunks, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    sizes = [len(c["text"]) for c in all_chunks]
    print(f"Documents: {len(list(RAW_DIR.glob('*.json')))}")
    print(f"Chunks:    {len(all_chunks)}")
    print(f"Min size:  {min(sizes)}")
    print(f"Max size:  {max(sizes)}")
    print(f"Mean size: {sum(sizes) // len(sizes)}")

    oversized = [c for c in all_chunks if len(c["text"]) > MAX_CHARS * 2]
    print(f"\nOversized chunks (>3000): {len(oversized)}")
    for c in sorted(oversized, key=lambda c: -len(c["text"]))[:10]:
        print(f"  {len(c['text']):>7}  {c['page_title']} > {c['section']}")

    tiny = [c for c in all_chunks if len(c["text"]) < MIN_CHARS]
    print(f"\nTiny chunks (<200): {len(tiny)}")

    print("\n--- Sample chunk ---\n")
    print(all_chunks[3]["text"][:600])


if __name__ == "__main__":
    main()