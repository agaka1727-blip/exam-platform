from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from parser import parse_questions, parse_docx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

QUESTIONS = []


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global QUESTIONS

    try:
        content = await file.read()
        filename = file.filename.lower()

        # DOCX файл
        if filename.endswith(".docx"):
            QUESTIONS = parse_docx(content)

        # TXT или другой текст
        else:
            text = content.decode("utf-8", errors="ignore")
            QUESTIONS = parse_questions(text)

        return {
            "status": "ok",
            "questions": len(QUESTIONS)
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/test")
def get_test():
    return QUESTIONS


@app.get("/")
def home():
    return {
        "status": "ok",
        "upload": "/upload",
        "test": "/test"
    }
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# --- база данных ---
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER,
            total INTEGER,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


# --- сохранение результата ---
@app.route("/submit", methods=["POST"])
def submit():
    data = request.json

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO results (score, total, date)
        VALUES (?, ?, ?)
    """, (
        data["score"],
        data["total"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})
