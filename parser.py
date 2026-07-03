from docx import Document

def parse_questions(text: str):
    lines = text.splitlines()

    return _parse_lines(lines)


def parse_docx(file_bytes):
    from io import BytesIO

    doc = Document(BytesIO(file_bytes))
    lines = []

    for p in doc.paragraphs:
        if p.text.strip():
            lines.append(p.text.strip())

    return _parse_lines(lines)


def _parse_lines(lines):
    questions = []
    current_q = None
    options = []

    def flush():
        nonlocal current_q, options
        if current_q and options:
            questions.append({
                "question": current_q,
                "options": options
            })
        current_q = None
        options = []

    for line in lines:
        line = line.strip()

        if not line:
            flush()
            continue

        # вопрос
        if current_q is None:
            current_q = line
            continue

        # варианты
        if line.startswith("+"):
            options.append({"text": line[1:].strip(), "correct": True})
        elif line.startswith("-"):
            options.append({"text": line[1:].strip(), "correct": False})
        else:
            # если вдруг продолжение вопроса
            if options:
                options[-1]["text"] += " " + line

    flush()
    return questions
