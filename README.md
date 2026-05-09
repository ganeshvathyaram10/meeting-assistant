🎙️ AI Meeting Assistant
An AI-powered meeting assistant that transforms transcripts or audio recordings into summaries, action items, and follow-up emails — automatically.


Live Demo: meeting-assistant1.netlify.app

✨ Features

🎙️ Audio Upload — Upload any .mp3, .wav, or .m4a file and Whisper transcribes it instantly
📋 Smart Summary — AI generates a concise 3-5 sentence meeting summary
✅ Action Items — Extracts tasks, owners, and due dates as structured data
📧 Email Draft — Auto-generates a professional follow-up email
🕐 Meeting History — All meetings saved and accessible anytime


🛠️ Tech Stack
LayerTechnologyFrontendReact + ViteBackendFastAPI (Python)DatabaseSQLiteSpeech-to-TextGroq Whisper Large v3AI / NLPLLaMA 3.3 70B via GroqFrontend DeployNetlifyBackend DeployRailway

🔗 AI Pipeline
Audio / Transcript Input
        ↓
  Whisper (speech-to-text)
        ↓
  LLM Call 1 → Summary
  LLM Call 2 → Action Items (structured JSON)
  LLM Call 3 → Email Draft (uses outputs of Call 1 & 2)
        ↓
  Saved to SQLite Database
        ↓
  Displayed in React Frontend

🚀 Run Locally
Backend
bashcd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Create a .env file:
GROQ_API_KEY=your_groq_api_key_here
Start the server:
bashuvicorn main:app --reload
Frontend
bashcd frontend
npm install
npm run dev
Visit http://localhost:5173

📁 Project Structure
meeting-assistant/
├── backend/
│   ├── main.py          # FastAPI routes
│   ├── ai_pipeline.py   # 3-step AI pipeline
│   ├── database.py      # SQLite setup
│   └── requirements.txt
└── frontend/
    └── src/
        └── App.jsx      # React frontend

🔑 Get a Free Groq API Key
Sign up at console.groq.com — it's free and takes 2 minutes.
