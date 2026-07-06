from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import random
import json
import os

# Импортируем парсер
from parser import parse_file_content

app = FastAPI()

# Настройка CORS для доступа с GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

QUESTIONS = []

# Загружаем кэш при старте
CACHE_FILE = "questions_cache.json"
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            QUESTIONS = json.load(f)
            print(f"✅ Загружено {len(QUESTIONS)} вопросов из кэша")
    except Exception as e:
        print(f"⚠️ Ошибка загрузки кэша: {e}")


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global QUESTIONS
    
    try:
        content = await file.read()
        
        # Используем парсер
        questions = parse_file_content(content, file.filename)
        
        if questions and len(questions) > 0:
            QUESTIONS = questions
            
            # Сохраняем в кэш
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(QUESTIONS, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "ok",
                "loaded_questions": len(QUESTIONS),
                "message": f"✅ Загружено {len(QUESTIONS)} вопросов",
                "first_question": QUESTIONS[0]["question"][:50] + "..." if QUESTIONS else ""
            }
        else:
            return {
                "status": "error",
                "message": "❌ Не найдено вопросов в файле. Проверьте формат."
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Ошибка: {str(e)}"
        }


@app.get("/test")
def test(limit: int = 30):
    """Возвращает случайные вопросы"""
    if not QUESTIONS:
        return []
    
    # Перемешиваем и возвращаем
    sample = random.sample(QUESTIONS, min(limit, len(QUESTIONS)))
    return sample


@app.get("/questions")
def get_all():
    """Возвращает все вопросы"""
    return QUESTIONS


@app.get("/count")
def count():
    """Количество вопросов"""
    return {"count": len(QUESTIONS)}


@app.get("/")
def home():
    return {
        "status": "ok",
        "questions_loaded": len(QUESTIONS),
        "endpoints": {
            "/upload": "POST - загрузить DOCX/TXT файл с вопросами",
            "/test": "GET - получить случайные 30 вопросов (можно ?limit=50)",
            "/questions": "GET - получить все вопросы",
            "/count": "GET - количество вопросов"
        }
    }


# Для локального запуска
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
