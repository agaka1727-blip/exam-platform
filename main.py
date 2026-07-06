from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from docx import Document
import io
import json
import random
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "questions.json"


# ---------- загрузка из файла ----------
def load_questions():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# ---------- сохранение ----------
def save_questions(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------- память ----------
QUESTIONS = load_questions()


# 📤 UPLOAD DOCX
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global QUESTIONS

    content = await file.read()
    doc = Document(io.BytesIO(content))

    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    QUESTIONS = []

    for i in range(len(lines)):
        if "?" in lines[i]:
            QUESTIONS.append({
                "question": lines[i],
                "options": [
                    lines[i+1] if i+1 < len(lines) else "",
                    lines[i+2] if i+2 < len(lines) else "",
                    lines[i+3] if i+3 < len(lines) else ""
                ],
                "correct": 0
            })

    save_questions(QUESTIONS)

    return {
        "status": "ok",
        "loaded_questions": len(QUESTIONS)
    }


# 📥 TEST
@app.get("/test")
def test():
    global QUESTIONS
    QUESTIONS = load_questions()

    if not QUESTIONS:
        return []

    return random.sample(QUESTIONS, min(30, len(QUESTIONS)))


# ❤️ HEALTH CHECK
@app.get("/")
def home():
    return {"status": "ok"}
