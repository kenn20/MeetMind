# MeetMind

**AI meeting intelligence that gives every team member a personalized summary.**

Upload a meeting recording and MeetMind transcribes it, extracts structured data (decisions, action items, topics), and generates tailored summaries for your Engineer, Designer, and PM — each enriched with git context and past meeting knowledge.

---

## How It Works

```
Audio/Video Upload
       │
       ▼
 ┌─────────────┐
 │ Transcription│  Google Gemini 2.5 Flash via OpenRouter
 │ + Diarization│  (speaker labels + timestamps)
 └──────┬──────┘
        │
   ┌────┴────┐
   │         │
   ▼         ▼
Ingest    Extraction
to Senso  Agent (LLM)
   │         │
   │    structured data:
   │    summary, topics,
   │    decisions, action
   │    items, speakers
   │         │
   └────┬────┘
        │
        ▼
 ┌──────────────────────────────────┐
 │     Three Persona Agents         │
 │  (each gets transcript + data)   │
 │                                  │
 │  🧑‍💻 Engineer  🎨 Designer  📋 PM  │
 │                                  │
 │  + git tools  + Senso search     │
 └──────────────┬───────────────────┘
                │
                ▼
         Web Dashboard
      (3-column layout)
```

Each persona agent receives **both** the raw transcript and the structured extraction, so they can quote specific timestamps and tie action items back to what was actually said.

## Features

- **Speaker diarization** with timestamps via Gemini 2.5 Flash
- **Structured extraction** — decisions, action items, topics, open questions, speaker mapping (Pydantic models)
- **Role-specific summaries** — Engineer gets technical action items and git context; Designer gets UX/UI tasks and accessibility notes; PM gets stakeholder actions, timeline, and risks
- **Git integration** — persona agents can pull recent commits, changed files, active branches, and file content from your repos
- **Knowledge base** — transcripts are ingested into Senso Context OS; agents can search past meetings for context
- **Web UI** — upload a recording and view all three summaries side-by-side with the raw transcript

## Tech Stack

| Component | Technology |
|---|---|
| Orchestration | [Railtracks](https://railtracks.dev) (agent flows with session persistence) |
| Transcription | Google Gemini 2.5 Flash via OpenRouter |
| LLM | DigitalOcean GPU Cloud — `openai-gpt-oss-120b` |
| Knowledge Base | Senso Context OS (ingest + semantic search) |
| Web Framework | Flask |
| Frontend | Vanilla HTML/CSS/JS + [marked.js](https://marked.js.org) |
| Data Models | Pydantic |

## Project Structure

```
meetmind/
├── agents/
│   ├── transcription.py    # Gemini transcription with speaker diarization
│   ├── extraction.py       # Structured data extraction (Pydantic output schema)
│   └── personas.py         # Engineer, Designer, PM persona agents
├── tools/
│   ├── git_tools.py        # Recent commits, changes, branches, file content
│   └── senso_tools.py      # Senso Context OS ingest + search
├── schemas/
│   └── models.py           # MeetingExtraction, Decision, ActionItem models
├── web/
│   ├── app.py              # Flask server
│   └── templates/
│       └── dashboard.html  # Dashboard UI
├── flow.py                 # Main orchestration flow (Railtracks)
├── repos.txt               # Project-to-repo-path mapping for git tools
├── requirements.txt
└── .env.example
```

## Getting Started

### Prerequisites

- Python 3.10+
- API keys for DigitalOcean GPU Cloud, OpenRouter, and Senso Context OS

### Setup

```bash
git clone https://github.com/kenn20/MeetMind.git
cd MeetMind/meetmind
pip install -r requirements.txt
cp .env.example .env
# Fill in your API keys in .env
```

### Environment Variables

| Variable | Description |
|---|---|
| `DigitalOceanAPIKey` | DigitalOcean GPU Cloud API key (LLM inference) |
| `OpenRouterKey` | OpenRouter API key (Gemini transcription) |
| `sensoAI` | Senso Context OS API key (knowledge base) |

### Run

**Web UI:**

```bash
python3 web/app.py
# Open http://localhost:5000
```

**CLI:**

```bash
python3 flow.py path/to/meeting.mp4
```

### Git Tools Configuration

Edit `repos.txt` to map project names to local repo paths:

```
myproject=/path/to/your/repo
```

Persona agents use this mapping to pull git context (recent commits, changed files, branches) relevant to each team member.

---

*Built at the Multi-Modal Frontier Hackathon 2026.*
