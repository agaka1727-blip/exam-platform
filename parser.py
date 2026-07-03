import re

def parse_questions(text: str):
    blocks = text.split("\n\n")
    questions = []

    for block in blocks:
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue

        question = lines[0]
        options = []

        for line in lines[1:]:
            if line.startswith("+"):
                options.append({"text": line[1:].strip(), "correct": True})
            elif line.startswith("-"):
                options.append({"text": line[1:].strip(), "correct": False})

        if question and options:
            questions.append({
                "question": question,
                "options": options
            })

    return questions
