from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from docx import Document
import io
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

QUESTIONS = []


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global QUESTIONS

    try:
        content = await file.read()
        doc = Document(io.BytesIO(content))

        lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

        QUESTIONS = []

        for i in range(len(lines)):
            if "?" in lines[i]:
                opts = []

                if i + 1 < len(lines):
                    opts.append(lines[i + 1])
                if i + 2 < len(lines):
                    opts.append(lines[i + 2])
                if i + 3 < len(lines):
                    opts.append(lines[i + 3])

                QUESTIONS.append({
                    "question": lines[i],
                    "options": opts,
                    "correct": 0
                })

        return {
            "status": "ok",
            "loaded_questions": len(QUESTIONS)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/test")
def test():
    if not QUESTIONS:
        return []

    return random.sample(QUESTIONS, min(30, len(QUESTIONS)))


@app.get("/")
def home():
    return {"status": "ok"}
