# ⚡ AI Proposal & RFP Engine

A Streamlit app that converts raw client RFPs and emails into high-converting enterprise proposals using Google Gemini's free-tier models. Includes a built-in "WordSpinner" humanizer that rewrites AI-sounding text into a natural enterprise tone.

> **Whitelabel / production build:** This is a production build for a specific company. The API key and the list of working models come from **environment variables / Streamlit secrets** — there is **no API key field**, **no model loading button**, and **no dropdown to load models** in the UI. Users only enter the client input and generate. All Streamlit branding (menu, footer, GitHub links) is hidden.

## Features

- Paste any client RFP / email and generate a complete enterprise proposal
- API key read automatically from `GEMINI_API_KEY` (env var or Streamlit secret) — no manual entry
- Pre-populated list of free Gemini models in a dropdown (no "Load Models" button)
- Configurable company portfolio & strengths context
- WordSpinner humanizer toggle with adjustable intensity (Standard B2B, Conversational Enterprise, Ultra-Natural / Direct)
- Selectable core focus capabilities to steer the proposal
- Download the generated proposal as a `.txt` file
- **No data storage:** client inputs and proposals are never saved; everything is wiped on refresh (no history)
- Dark, modern UI theme

## Prerequisites

- Python 3.12+
- A free [Google Gemini API key](https://aistudio.google.com/apikey) (free tier — no credit card needed)

## Setup & Run (Local)

```bash
# 1. Clone or navigate into the project
cd ProposalForge

# 2. Create a virtual environment
python3 -m venv env

# 3. Activate it
source env/bin/activate    # Linux / macOS
# .\env\Scripts\activate  # Windows (PowerShell)

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set the API key (via env var)
export GEMINI_API_KEY="your-gemini-api-key"
# OPTIONAL overrides:
# export API_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
# export MODELS="gemini-3.5-flash,gemini-3.5-flash-lite,gemini-2.5-flash"

# 6. Launch the app
streamlit run main.py
```

Your browser will open automatically at `http://localhost:8501`.

## Usage

1. The API key is already configured server-side — no key entry needed.
2. Pick an AI engine from the pre-populated dropdown.
3. Configure the **WordSpinner** humanizer settings and review/update the company context.
4. In the main panel, enter the client name, paste the RFP/requirements, select the core capabilities, and click **🚀 Generate Enterprise Proposal**.
5. The structured proposal appears on the right — **copy it or download it as a `.txt` file**. Nothing is saved, so be sure to save before refreshing.

## No-Data-Storage Policy

- Client inputs and generated proposals are **not stored** on the server, in a database, or in cookies.
- Data lives only in the current browser session and **is wiped on refresh**.
- There is **no history** feature. Always copy or download the output `.txt` before leaving the page.

## How It Works

The app injects a Principal-Enterprise-Architect prompt (plus optional anti-buzzword humanizer rules) into the selected model and returns a proposal structured as:

1. Problem Breakdown & Executive Summary
2. Proposed Solution & AI Agent Architecture
3. 4-Week Pilot Roadmap & Key Deliverables
4. Why Our Company
5. Next Steps

## Project Structure

```
ProposalForge/
├── main.py            # Streamlit app entry point (env-driven API key)
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variable reference
├── env/               # Local Python virtual environment (not committed)
└── README.md
```

## Notes

- Requires an internet connection to reach the Gemini API.
- The API key is read from `GEMINI_API_KEY` (env var or Streamlit secret) only; it is never stored on disk.
- Gemini's free tier includes `gemini-3.5-flash`, `gemini-3.5-flash-lite`, and `gemini-2.5-flash` with a generous daily quota — effectively unlimited for proposal generation. If `MODELS` is not set, these defaults are shown in the dropdown.