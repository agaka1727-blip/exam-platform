from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

# 🌐 CORS (чтобы сайт работал с GitHub Pages)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧠 Хранилище вопросов (в памяти сервера)
QUESTIONS = []


# 📤 ЗАГРУЗКА ФАЙЛА
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global QUESTIONS

    content = await file.read()
    text = content.decode("utf-8", errors="ignore")

    lines = text.split("\n")

    QUESTIONS = []

    # 🧩 супер простой парсер (fallback)
    for i in range(len(lines)):
        if "?" in lines[i]:
            QUESTIONS.append({
                "question": lines[i].strip(),
                "options": [
                    lines[i+1].strip() if i+1 < len(lines) else "",
                    lines[i+2].strip() if i+2 < len(lines) else "",
                    lines[i+3].strip() if i+3 < len(lines) else ""
                ],
                "correct": 0
            })

    return {
        "status": "ok",
        "loaded_questions": len(QUESTIONS)
    }


# 📥 ОТДАЧА ВОПРОСОВ ДЛЯ ЭКЗАМЕНА
@app.get("/test")
def get_test():
    if not QUESTIONS:
        return []

    sample = random.sample(QUESTIONS, min(30, len(QUESTIONS)))

    return sample


# ❤️ проверка что сервер жив
@app.get("/")
def home():
    return {"status": "server is running"}
