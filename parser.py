from docx import Document
from io import BytesIO
import re


def parse_questions(text: str):
    """
    Парсинг обычного текста (TXT)
    """
    lines = text.splitlines()
    return _parse_lines(lines)


def parse_docx(file_bytes):
    """
    Парсинг DOCX файла
    """
    doc = Document(BytesIO(file_bytes))
    lines = []

    for p in doc.paragraphs:
        text = p.text.strip()
        if text:
            lines.append(text)

    return _parse_lines(lines)


def _parse_lines(lines):
    questions = []
    current_question = None
    options = []

    def save_question():
        nonlocal current_question, options

        if current_question:
            questions.append({
                "question": current_question.strip(),
                "options": options
            })

        current_question = None
        options = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # 🔹 начало нового вопроса (1., 2), 3. и т.д.)
        if re.match(r"^\d+[\)\.]", line):
            save_question()
            current_question = line
            continue

        # если вопрос ещё не начался
        if current_question is None:
            current_question = line
            continue

        # 🔹 правильный ответ
        if line.startswith("+"):
            options.append({
                "text": line[1:].strip(),
                "correct": True
            })

        # 🔹 неправильный ответ
        elif line.startswith("-"):
            options.append({
                "text": line[1:].strip(),
                "correct": False
            })

        # 🔹 если это продолжение вопроса
        else:
            current_question += " " + line

    save_question()
    return questions
