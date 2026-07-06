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
    """Основная логика парсинга с категориями"""
    questions = []
    current_question = None
    options = []
    correct_index = None
    current_category = "Общие вопросы"
    i = 0
    
    # Определяем категории по заголовкам
    category_patterns = {
        "Уголовно-процессуальное": ["уголовно-процессуальному", "УПК"],
        "Уголовно-исполнительное": ["уголовно-исполнительному"],
        "Трудовое": ["трудовому праву", "Трудовой кодекс"],
        "Семейное": ["семейному праву", "Семейный кодекс"],
        "Международное": ["международному праву"],
        "Конституционное": ["конституционному праву", "Конституция"],
        "Уголовное": ["уголовному праву", "Уголовный кодекс"],
        "Исполнительное производство": ["исполнительному производству"],
        "Таможенное": ["таможенному праву"],
        "Избирательное": ["избирательному праву"],
        "Гражданско-процессуальное": ["гражданско-процессуальному", "ГПК"],
        "Гражданское": ["гражданскому праву", "Гражданский кодекс"],
        "Земельное": ["земельному праву", "Земельный кодекс"],
        "Природоресурсное": ["природоресурсному праву"],
        "Административно-процессуальное": ["административно-процессуальному", "АПК"],
        "Гендерное": ["гендерному праву"],
        "Адвокатура": ["адвокатуре"],
        "Прокуратура": ["прокуратуре"],
        "Цифровой кодекс": ["цифровому кодексу"],
        "Досудебные способы": ["досудебным способам", "медиации"],
    }
    
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
        
        # Проверяем, является ли строка заголовком категории
        line_lower = line.lower()
        for category, keywords in category_patterns.items():
            for keyword in keywords:
                if keyword.lower() in line_lower and len(line) < 100:
                    current_category = category
                    i += 1
                    break
            else:
                continue
            break
        else:
            # Проверяем, является ли строка вопросом
            is_question = (
                "?" in line or 
                re.match(r'^\d+[\)\.]\s*', line) or
                any(word in line_lower for word in ['какой', 'что', 'где', 'когда', 'кто', 'как', 'почему', 'сколько', 'в каких', 'в каком', 'какие', 'кем', 'кому', 'кого'])
            )
            
            if re.match(r'^\d+[\)\.]\s*', line):
                if current_question and options:
                    if correct_index is None:
                        correct_index = 0
                    questions.append({
                        "category": current_category,
                        "question": current_question.strip(),
                        "options": options[:4],
                        "correct": correct_index
                    })
                current_question = re.sub(r'^\d+[\)\.]\s*', '', line)
                options = []
                correct_index = None
                i += 1
                continue
            
            if current_question is None:
                if is_question:
                    current_question = line
                    options = []
                    correct_index = None
                    i += 1
                else:
                    i += 1
                continue
            
            is_option = False
            
            if line.startswith("+") or line.startswith("*"):
                option_text = line[1:].strip()
                option_text = re.sub(r';$', '', option_text).strip()
                options.append(option_text)
                correct_index = len(options) - 1
                is_option = True
                
            elif line.startswith("-") or line.startswith("•") or line.startswith("·"):
                option_text = line[1:].strip()
                option_text = re.sub(r';$', '', option_text).strip()
                options.append(option_text)
                is_option = True
                
            elif re.match(r'^[а-яa-z]\)', line) or re.match(r'^\d+\)', line):
                option_text = re.sub(r'^[а-яa-z\d]\)\s*', '', line)
                option_text = re.sub(r';$', '', option_text).strip()
                options.append(option_text)
                is_option = True
            
            if not is_option:
                current_question += " " + line
            
            i += 1
    
    if current_question and options:
        if correct_index is None:
            correct_index = 0
        questions.append({
            "category": current_category,
            "question": current_question.strip(),
            "options": options[:4],
            "correct": correct_index
        })
    
    return questions


def parse_file_content(file_content: bytes, filename: str) -> List[Dict[str, Any]]:
    """Универсальная функция для парсинга загруженного файла"""
    if filename.endswith('.docx'):
        return parse_docx(file_content)
    else:
        try:
            text = file_content.decode('utf-8')
        except UnicodeDecodeError:
            text = file_content.decode('windows-1251')
        return parse_questions(text)
