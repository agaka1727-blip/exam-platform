from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from parser import parse_questions

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
    text = content.decode("utf-8", errors="ignore")
    QUESTIONS = parse_questions(text)
    return {"questions": len(QUESTIONS)}

@app.get("/test")
def get_test():
    return QUESTIONS


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Exam Platform</title>
        <style>
            body { font-family: Arial; background:#f4f4f4; padding:20px; }
            .card { background:white; padding:20px; border-radius:10px; max-width:700px; margin:auto; }
            button { padding:10px; margin-top:10px; cursor:pointer; }
            .question { font-size:18px; margin-bottom:10px; }
            .option { display:block; margin:5px 0; }
        </style>
    </head>
    <body>

    <div class="card">
        <h2>Экзамен система</h2>

        <h3>1. Загрузите файл с вопросами</h3>

        <input type="file" id="file" />
        <button onclick="uploadFile()">Загрузить</button>

        <hr>

        <button onclick="loadTest()">Начать тест</button>

        <div id="test"></div>
    </div>

    <script>
    let questions = [];
    let index = 0;
    let score = 0;

    async function uploadFile() {
        const fileInput = document.getElementById("file");
        const file = fileInput.files[0];

        if (!file) {
            alert("Выберите файл");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        alert("Загружено вопросов: " + data.questions);
    }

    async function loadTest() {
        const res = await fetch("/test");
        questions = await res.json();

        index = 0;
        score = 0;

        showQuestion();
    }

    function showQuestion() {
        if (index >= questions.length) {
            document.getElementById("test").innerHTML =
                "<h3>Результат: " + score + " / " + questions.length + "</h3>";
            return;
        }

        const q = questions[index];

        let html = "<div class='question'>" + q.question + "</div>";

        q.options.forEach(opt => {
            html += `
                <label class='option'>
                    <input type='radio' name='opt' value='${opt.correct}'>
                    ${opt.text}
                </label>
            `;
        });

        html += "<button onclick='next()'>Далее</button>";

        document.getElementById("test").innerHTML = html;
    }

    function next() {
        const selected = document.querySelector('input[name="opt"]:checked');

        if (selected && selected.value === "true") {
            score++;
        }

        index++;
        showQuestion();
    }
    </script>

    </body>
    </html>
    """
