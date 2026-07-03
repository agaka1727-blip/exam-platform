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
