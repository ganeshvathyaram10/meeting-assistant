from fastapi import FastAPI, HTTPException, UploadFile, File
import tempfile, os
from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

from database import init_db, get_db
from ai_pipeline import run_pipeline

app = FastAPI()

# Allow React frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup():
    init_db()
    print("✅ Database ready")


# ── Request model ──────────────────────────────────────────────
class MeetingRequest(BaseModel):
    title: str
    transcript: str


# ── POST /meetings — process a new meeting ─────────────────────
@app.post("/meetings")
def create_meeting(req: MeetingRequest):
    if len(req.transcript.strip()) < 50:
        raise HTTPException(status_code=400, detail="Transcript too short")

    # Run the 3-step AI pipeline
    result = run_pipeline(req.transcript)

    # Save to database
    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO meetings (title, transcript, summary, action_items, email_draft)
           VALUES (?, ?, ?, ?, ?)""",
        (
            req.title,
            req.transcript,
            result["summary"],
            json.dumps(result["action_items"]),  # list → JSON string
            result["email_draft"],
        )
    )
    conn.commit()
    meeting_id = cursor.lastrowid
    conn.close()

    return {
        "id": meeting_id,
        "title": req.title,
        "summary": result["summary"],
        "action_items": result["action_items"],
        "email_draft": result["email_draft"]
    }


# ── GET /meetings — fetch all past meetings ────────────────────
@app.get("/meetings")
def get_meetings():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, title, summary, created_at FROM meetings ORDER BY created_at DESC"
    ).fetchall()
    conn.close()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "summary": row["summary"],
            "created_at": row["created_at"]
        }
        for row in rows
    ]


# ── GET /meetings/{id} — fetch one meeting ─────────────────────
@app.get("/meetings/{meeting_id}")
def get_meeting(meeting_id: int):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM meetings WHERE id = ?", (meeting_id,)
    ).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return {
        "id": row["id"],
        "title": row["title"],
        "transcript": row["transcript"],
        "summary": row["summary"],
        "action_items": json.loads(row["action_items"]),  # JSON string → list
        "email_draft": row["email_draft"],
        "created_at": row["created_at"]
    }
# ── POST /transcribe — convert audio to text ───────────────────
@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    # Save uploaded file temporarily to disk
    suffix = os.path.splitext(file.filename)[1]  # e.g. .mp3, .wav, .m4a
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                response_format="text"
            )
        return {"transcript": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)  # delete temp file