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

    content = await file.read()
    filename = file.filename.lower()

    if filename.endswith(".docx"):
        QUESTIONS = parse_docx(content)
    else:
        text = content.decode("utf-8", errors="ignore")
        QUESTIONS = parse_questions(text)

    return {"questions": len(QUESTIONS)}

@app.get("/test")
def get_test():
    return QUESTIONS

@app.get("/")
def home():
    return {"status": "ok"}
