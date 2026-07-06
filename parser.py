from docx import Document
from io import BytesIO
import re
import json
from typing import List, Dict, Any


def parse_questions(text: str) -> List[Dict[str, Any]]:
    """Парсинг обычного текста (TXT)"""
    lines = text.splitlines()
    return _parse_lines(lines)


def parse_docx(file_bytes: bytes) -> List[Dict[str, Any]]:
    """Парсинг DOCX файла"""
    try:
        doc = Document(BytesIO(file_bytes))
        lines = []

        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                lines.append(text)

        return _parse_lines(lines)
    except Exception as e:
        print(f"Ошибка парсинга DOCX: {e}")
        return []


def _parse_lines(lines: List[str]) -> List[Dict[str, Any]]:
    """Основная логика парсинга"""
    questions = []
    current_question = None
    options = []
    correct_index = None

    def save_question():
        nonlocal current_question, options, correct_index

        if current_question and options:
            if correct_index is None:
                correct_index = 0
            
            questions.append({
                "question": current_question.strip(),
                "options": options,
                "correct": correct_index
            })

        return None, [], None

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Новый вопрос (1., 2), 3. и т.д.)
        if re.match(r"^\d+[\)\.]\s*", line):
            if current_question:
                save_question()
                current_question = None
                options = []
                correct_index = None
            
            # Убираем номер
            current_question = re.sub(r"^\d+[\)\.]\s*", "", line)
            continue

        if current_question is None:
            current_question = line
            continue

        is_option = False
        
        # Правильный ответ
        if line.startswith("+") or line.startswith("*"):
            option_text = line[1:].strip()
            options.append(option_text)
            correct_index = len(options) - 1
            is_option = True
            
        # Неправильный ответ
        elif line.startswith("-") or line.startswith("•") or line.startswith("·"):
            option_text = line[1:].strip()
            options.append(option_text)
            is_option = True
            
        # Вариант с буквой или цифрой
        elif re.match(r"^[а-яa-z]\)", line) or re.match(r"^\d+\)", line):
            option_text = re.sub(r"^[а-яa-z\d]\)\s*", "", line)
            options.append(option_text)
            is_option = True

        if not is_option:
            current_question += " " + line

    if current_question:
        save_question()
    
    return questions


def parse_file_content(file_content: bytes, filename: str) -> List[Dict[str, Any]]:
    """Универсальная функция для парсинга загруженного файла"""
    if filename.endswith('.docx'):
        return parse_docx(file_content)
    else:
        try:
            text = file_content.decode('utf-8')
            return parse_questions(text)
        except UnicodeDecodeError:
            # Пробуем другую кодировку
            text = file_content.decode('windows-1251')
            return parse_questions(text)


def parse_and_save(file_path: str, output_path: str = "questions.json"):
    """Утилита для парсинга файла и сохранения в JSON"""
    with open(file_path, 'rb') as f:
        content = f.read()
    
    if file_path.endswith('.docx'):
        questions = parse_docx(content)
    else:
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            text = content.decode('windows-1251')
        questions = parse_questions(text)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Сохранено {len(questions)} вопросов в {output_path}")
    return questions


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        output = sys.argv[2] if len(sys.argv) > 2 else "questions.json"
        parse_and_save(file_path, output)
    else:
        print("📖 Использование: python parser.py <путь_к_файлу> [путь_к_json]")
        print("Пример: python parser.py questions.docx questions.json")
