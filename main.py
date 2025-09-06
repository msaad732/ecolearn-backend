from fastapi import FastAPI, UploadFile, File, Form, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os, uuid, requests, base64, json, asyncio
from dotenv import load_dotenv
import re

# --- Database Setup ---
from sqlalchemy import create_engine, Column, Integer, String, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# --- App setup ---
app = FastAPI(title="EcoLearn AI Backend")
router = APIRouter()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static directory for media
MEDIA_DIR = os.path.join(os.path.dirname(__file__), "media")
os.makedirs(MEDIA_DIR, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# --- Groq API Setup ---
GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_BASE_URL = "https://api.groq.com/openai/v1"


# In-memory conversation store
conversations = {}

# --- DB Setup ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leaderboard.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Leaderboard(Base):
    __tablename__ = "leaderboard"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    score = Column(Integer)

Base.metadata.create_all(bind=engine)

# Active quiz store
active_quizzes = {}

# --- Models ---
class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    age_level: str = "12"
    tts: bool = True

class CarbonRequest(BaseModel):
    electricity: float  # kWh per month
    transport: float    # km per week
    diet: str           # veg, mixed, meat

class RecycleRequest(BaseModel):
    image_base64: str

class QuizSubmission(BaseModel):
    username: str
    answers: str

# --- Helpers ---
def validate_response(response: str, language: str, age_level: str) -> str:
    return response

def grok_chat_completion(message: str, language: str, age_level: str, user_id: str = "user-1") -> str:
    if user_id not in conversations:
        conversations[user_id] = [{"role": "system", "content": f"Respond in {language}, for age level {age_level}."}]
    conversations[user_id].append({"role": "user", "content": message})

    try:
        headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": conversations[user_id],
            "max_tokens": 1500,
            "temperature": 0.5,
        }
        response = requests.post(f"{GROK_BASE_URL}/chat/completions", headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            reply = data['choices'][0]['message']['content'].strip()
            validated_reply = validate_response(reply, language, age_level)
            conversations[user_id].append({"role": "assistant", "content": validated_reply})
            return validated_reply
        else:
            return f"⚠️ API Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"⚠️ Exception: {str(e)}"

def grok_tts(text: str, language: str) -> str:
    return None  # placeholder

def grok_stt_from_audiobytes(audio_bytes: bytes, language: str) -> str:
    try:
        temp_filename = f"temp_{uuid.uuid4().hex}.webm"
        temp_path = os.path.join(MEDIA_DIR, temp_filename)
        with open(temp_path, "wb") as f:
            f.write(audio_bytes)

        headers = {"Authorization": f"Bearer {GROK_API_KEY}"}
        with open(temp_path, "rb") as audio_file:
            files = {"file": ("audio.webm", audio_file, "audio/webm")}
            data = {"model": "whisper-large-v3", "language": language}
            response = requests.post(f"{GROK_BASE_URL}/audio/transcriptions", headers=headers, files=files, data=data)

        os.remove(temp_path)
        if response.status_code == 200:
            return response.json().get('text', "Sorry, I couldn't understand the audio.")
        else:
            return "Sorry, I couldn't understand the audio."
    except Exception:
        return "Sorry, I couldn't understand the audio."

# --- Routes ---
@app.get("/")
def health():
    return {"msg": "EcoLearn backend is running with Groq Whisper + LLaMA-3 + DB leaderboard!"}

@app.post("/chat")
def chat(req: ChatRequest):
    answer_text = grok_chat_completion(req.message, req.language, req.age_level)
    audio_url = grok_tts(answer_text, req.language) if req.tts else None
    return JSONResponse({"text": answer_text, "audio_url": audio_url})

@app.post("/stt")
async def stt(language: str = Form("en"), audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    transcript = grok_stt_from_audiobytes(audio_bytes, language)
    return JSONResponse({"text": transcript})

@app.post("/carbon-footprint")
def carbon_footprint(req: CarbonRequest):
    user_prompt = f"""
The user has shared their lifestyle data:
- Electricity use: {req.electricity} kWh per month
- Transport: {req.transport} km per week
- Diet: {req.diet}

Provide exactly 3 practical ways to reduce their carbon footprint.
Only list the 3 points as bullet points. 
Do NOT add any introductory or concluding sentences. 
Do NOT use any markdown, bold, or asterisks.
Just:
- Suggestion 1
- Suggestion 2
- Suggestion 3
"""
    tips_text = grok_chat_completion(user_prompt, "en", "adult", user_id="carbon-footprint")
    tips = [line.strip("-•* ").strip() for line in tips_text.split("\n") if line.strip()]
    return {"tips": tips[:3]}

@app.post("/recycle")
async def recycle_image(req: RecycleRequest):
    try:
        img_bytes = base64.b64decode(req.image_base64)

        # Call Hugging Face Space
        space_url = "https://ms732-recycle-items.hf.space/api/predict"
        hf_resp = requests.post(space_url, json={"data": [req.image_base64]})
        hf_json = hf_resp.json()
        print("HF Space Response:", hf_json)

        label = hf_json["data"][0] if "data" in hf_json else "plastic item"

        prompt = f"""Please summarize recycling and reuse suggestions for {label} in under 5 sentences.
        Dont write intro just directly give the sentences. Also bold main points. 
        Please dont say about general plastics or other types of plastics.
        Only give points about the specific item the label that is provided.
        Also mention how it can be recycled and reused like a DIY project or something which can be done at home.
        Make it easy to understand and use. """

        ai_suggestion = grok_chat_completion(prompt, language="en", age_level="12")

        return JSONResponse({"label": label, "ai_suggestion": ai_suggestion})

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JSONResponse({"error": str(e)}, status_code=500)

# --- Quiz Endpoints ---
@router.post("/start")
def start_quiz(username: str = Form(...)):
    prompt = """
    Generate 5 multiple choice quiz questions about recycling, climate change, or sustainability. 
    Each should have 4 options (A, B, C, D) and specify the correct one.
    The format should be exactly like this, without any other text or introduction:
    Q1. What is recycling?
    A. Reusing materials
    B. Burning waste
    C. Throwing waste
    D. Making new from oil
    Answer: A

    Q2. What is a carbon footprint?
    A. A type of shoe
    B. The total greenhouse gas emissions caused by a person or organization
    C. The amount of carbon in a person's body
    D. A dance move
    Answer: B
    """
    quiz_text = grok_chat_completion(prompt, "en", "12", user_id=username)

    questions = []
    # Split the response into individual question blocks
    blocks = re.split(r'Q\d+\.', quiz_text, flags=re.IGNORECASE)
    
    for block in blocks:
        if not block.strip():
            continue
        
        lines = block.strip().split("\n")
        
        q = {"question": None, "options": [], "answer": None}
        
        # The first line should be the question
        q["question"] = lines[0].strip()
        
        # The next 4 lines should be the options
        options_lines = lines[1:5]
        for opt_line in options_lines:
            if re.match(r"^[A-D]\.\s", opt_line):
                q["options"].append(opt_line.strip())
        
        # The last line should be the answer
        answer_line = lines[-1].strip()
        ans_match = re.search(r"Answer:\s*([A-D])", answer_line, re.IGNORECASE)
        if ans_match:
            q["answer"] = ans_match.group(1).upper()
            
        if q["question"] and len(q["options"]) == 4 and q["answer"]:
            questions.append(q)

    # Ensure exactly 5 questions
    questions = questions[:5]
    
    active_quizzes[username] = questions
    return {"questions": questions}

@router.post("/submit")
def submit_quiz(submission: QuizSubmission):
    db = SessionLocal()
    try:
        # Get the correct questions from the active quiz store
        correct_questions = active_quizzes.get(submission.username)
        if not correct_questions:
            return JSONResponse({"error": "Quiz session not found. Please start a new quiz."}, status_code=404)

        # Parse the user's answers
        user_answers = json.loads(submission.answers)

        score = 0
        total = len(correct_questions)

        # Compare user answers to correct answers
        correct_ans_dict = {f"q{idx}": q["answer"] for idx, q in enumerate(correct_questions)}

        for answer in user_answers:
            q_index = answer["q"]
            user_ans_letter = answer["ans"]
            
            if f"q{q_index}" in correct_ans_dict and user_ans_letter == correct_ans_dict[f"q{q_index}"]:
                score += 1
        
        # Save score to the leaderboard
        db_user = db.query(Leaderboard).filter(Leaderboard.username == submission.username).first()
        if db_user:
            db_user.score = score
        else:
            db_user = Leaderboard(username=submission.username, score=score)
            db.add(db_user)
        
        db.commit()
        
        # Clear the quiz from memory after submission
        if submission.username in active_quizzes:
            del active_quizzes[submission.username]
            
        return JSONResponse({"score": score, "total": total})
    except Exception as e:
        db.rollback()
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        db.close()

@router.get("/leaderboard")
def get_leaderboard():
    db = SessionLocal()
    try:
        leaderboard = db.query(Leaderboard).order_by(desc(Leaderboard.score)).limit(10).all()
        
        return JSONResponse({"leaderboard": [{"username": entry.username, "score": entry.score} for entry in leaderboard]})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        db.close()

# Include the quiz router
app.include_router(router, prefix="/quiz")

# --- Share: simple image upload to serve a public URL ---
@app.post("/share/upload")
async def share_upload(request: Request, image: UploadFile = File(...)):
    try:
        ext = os.path.splitext(image.filename or "")[1].lower() or ".png"
        if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
            ext = ".png"
        fname = f"share_{uuid.uuid4().hex}{ext}"
        path = os.path.join(MEDIA_DIR, fname)
        content = await image.read()
        with open(path, "wb") as f:
            f.write(content)
        base_url = str(request.base_url).rstrip("/")
        rel_url = f"/media/{fname}"
        abs_url = f"{base_url}{rel_url}"
        return {"url": rel_url, "absolute_url": abs_url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# --- Run ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
