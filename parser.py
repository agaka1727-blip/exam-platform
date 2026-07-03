def parse_questions(text: str):
    lines = text.splitlines()

    questions = []
    current_q = None
    options = []

    for line in lines:
        line = line.strip()

        if not line:
            if current_q and options:
                questions.append({
                    "question": current_q,
                    "options": options
                })
            current_q = None
            options = []
            continue

        if current_q is None:
            current_q = line
        else:
            if line.startswith("+"):
                options.append({"text": line[1:].strip(), "correct": True})
            elif line.startswith("-"):
                options.append({"text": line[1:].strip(), "correct": False})

    if current_q and options:
        questions.append({
            "question": current_q,
            "options": options
        })

    return questions
