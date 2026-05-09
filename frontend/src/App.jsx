import { useState, useEffect } from "react"
import axios from "axios"

const API = "https://meeting-assistant-backend-production-3af8.up.railway.app"

export default function App() {
  const [title, setTitle] = useState("")
  const [transcript, setTranscript] = useState("")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [history, setHistory] = useState([])

  // Load past meetings on page load
  useEffect(() => {
    axios.get(`${API}/meetings`)
      .then(res => setHistory(res.data))
      .catch(() => {})
  }, [])
  async function handleAudioUpload(e) {
    const file = e.target.files[0]
    if (!file) return
  
    setError("")
    setLoading(true)
    setTranscript("")
  
    try {
      const formData = new FormData()
      formData.append("file", file)
  
      const res = await axios.post(`${API}/transcribe`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      })
      setTranscript(res.data.transcript)
    } catch (err) {
      setError("Audio transcription failed. Try a smaller file.")
    } finally {
      setLoading(false)
    }
  }

  async function handleSubmit() {
    if (!title.trim() || !transcript.trim()) {
      setError("Please fill in both fields.")
      return
    }
    setError("")
    setLoading(true)
    setResult(null)

    try {
      const res = await axios.post(`${API}/meetings`, { title, transcript })
      setResult(res.data)
      // Add new meeting to history at the top
      setHistory(prev => [{ id: res.data.id, title: res.data.title, summary: res.data.summary, created_at: new Date().toISOString() }, ...prev])
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong.")
    } finally {
      setLoading(false)
    }
  }

  async function loadMeeting(id) {
    setLoading(true)
    setResult(null)
    try {
      const res = await axios.get(`${API}/meetings/${id}`)
      setResult(res.data)
      setTitle(res.data.title)
      setTranscript(res.data.transcript)
    } catch {
      setError("Could not load meeting.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>🎙️ AI Meeting Assistant</h1>
      <p className="subtitle">Paste a transcript → get summary, action items & follow-up email</p>

      {/* Input Card */}
      <div className="card">
        <h2>New Meeting</h2>
        <input
          placeholder="Meeting title (e.g. Product Launch Sync)"
          value={title}
          onChange={e => setTitle(e.target.value)}
        />
        {/* Audio Upload */}
<div style={{ marginBottom: 12 }}>
  <label style={{
    display: "block",
    marginBottom: 6,
    fontSize: "0.9rem",
    color: "#666"
  }}>
    🎙️ Upload audio (mp3, wav, m4a) — or paste transcript manually below
  </label>
  <input
    type="file"
    accept=".mp3,.wav,.m4a,.ogg,.webm"
    onChange={handleAudioUpload}
    style={{ padding: 0, border: "none", background: "none" }}
  />
</div>
        <textarea
          placeholder="Paste your meeting transcript here..."
          rows={8}
          value={transcript}
          onChange={e => setTranscript(e.target.value)}
        />
        {error && <p className="error">{error}</p>}
        <button onClick={handleSubmit} disabled={loading}>
          {loading ? "⏳ Processing..." : "✨ Analyze Meeting"}
        </button>
      </div>

      {/* Results */}
      {result && (
        <>
          <div className="card">
            <h2>📋 Summary</h2>
            <p style={{ lineHeight: 1.7 }}>{result.summary}</p>
          </div>

          <div className="card">
            <h2>✅ Action Items</h2>
            {result.action_items.map((item, i) => (
              <div className="action-item" key={i}>
                <span>{item.task}</span>
                <div style={{ display: "flex", gap: 8 }}>
                  <span className="tag">👤 {item.owner}</span>
                  <span className="tag">📅 {item.due_date}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="card">
            <h2>📧 Email Draft</h2>
            <div className="email-box">{result.email_draft}</div>
          </div>
        </>
      )}

      {/* Past Meetings */}
      {history.length > 0 && (
        <div className="card">
          <h2>🕐 Past Meetings</h2>
          {history.map(m => (
            <div className="history-item" key={m.id} onClick={() => loadMeeting(m.id)}>
              <div>{m.title}</div>
              <div className="history-date">{new Date(m.created_at).toLocaleDateString()}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}