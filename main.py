from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from docx import Document
import random
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

QUESTIONS = []


# 📤 UPLOAD DOCX (ПРАВИЛЬНЫЙ ПАРСЕР)
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global QUESTIONS

    content = await file.read()

    doc = Document(io.BytesIO(content))

    lines = []
    for p in doc.paragraphs:
        if p.text.strip():
            lines.append(p.text.strip())

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

    return {
        "status": "ok",
        "loaded_questions": len(QUESTIONS)
    }


# 📥 TEST
@app.get("/test")
def get_test():
    if not QUESTIONS:
        return []

    return random.sample(QUESTIONS, min(30, len(QUESTIONS)))


# ❤️ health check
@app.get("/")
def home():
    return {"status": "server running"}
