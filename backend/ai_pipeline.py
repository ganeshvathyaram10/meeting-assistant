import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

# ── Call 1: Summarize ──────────────────────────────────────────
def summarize_transcript(transcript: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an expert meeting summarizer. Write clear, concise summaries in 3-5 sentences covering the main topics, decisions, and outcomes."
            },
            {
                "role": "user",
                "content": f"Summarize this meeting transcript:\n\n{transcript}"
            }
        ]
    )
    return response.choices[0].message.content


# ── Call 2: Extract Action Items (structured JSON) ─────────────
def extract_action_items(transcript: str) -> list:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": """You extract action items from meeting transcripts.
You MUST respond with ONLY a JSON array, no explanation, no markdown.
Each item must have: "task", "owner", "due_date".
If unknown, use "TBD".

Example:
[
  {"task": "Send report", "owner": "Alice", "due_date": "Friday"},
  {"task": "Book venue", "owner": "TBD", "due_date": "TBD"}
]"""
            },
            {
                "role": "user",
                "content": f"Extract all action items from this transcript:\n\n{transcript}"
            }
        ]
    )
    raw = response.choices[0].message.content.strip()

    # Clean up in case AI wraps in markdown code blocks
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw)


# ── Call 3: Draft Follow-up Email ─────────────────────────────
def draft_email(summary: str, action_items: list) -> str:
    action_text = "\n".join(
        [f"- {item['task']} (Owner: {item['owner']}, Due: {item['due_date']})"
         for item in action_items]
    )
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You write professional but friendly follow-up emails after meetings. Keep them concise and clear."
            },
            {
                "role": "user",
                "content": f"""Write a follow-up email based on this meeting summary and action items.

Summary:
{summary}

Action Items:
{action_text}"""
            }
        ]
    )
    return response.choices[0].message.content


# ── Master function: runs all 3 calls in sequence ─────────────
def run_pipeline(transcript: str) -> dict:
    print("⏳ Step 1: Summarizing...")
    summary = summarize_transcript(transcript)

    print("⏳ Step 2: Extracting action items...")
    action_items = extract_action_items(transcript)

    print("⏳ Step 3: Drafting email...")
    email_draft = draft_email(summary, action_items)

    print("✅ Pipeline complete!")
    return {
        "summary": summary,
        "action_items": action_items,
        "email_draft": email_draft
    }
