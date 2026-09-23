# ⚡ AI Proposal & RFP Engine

A Streamlit app that converts raw client RFPs and emails into high-converting enterprise proposals using any OpenAI-compatible AI model (Claude, GPT, Llama) via OpenRouter. Includes a built-in "WordSpinner" humanizer that rewrites AI-sounding text into a natural enterprise tone.

> **Whitelabel / production build:** This is a production build for a specific company. The API key and the list of working models come from **environment variables / Streamlit secrets** — there is **no API key field**, **no model loading button**, and **no dropdown to load models** in the UI. Users only enter the client input and generate. All Streamlit branding (menu, footer, GitHub links) is hidden.

## Features

- Paste any client RFP / email and generate a complete enterprise proposal
- API key read automatically from `OPENROUTER_API_KEY` (env var or Streamlit secret) — no manual entry
- Pre-populated list of working models in a dropdown (no "Load Models" button)
- Configurable company portfolio & strengths context
- WordSpinner humanizer toggle with adjustable intensity (Standard B2B, Conversational Enterprise, Ultra-Natural / Direct)
- Selectable core focus capabilities to steer the proposal
- Download the generated proposal as a `.txt` file
- **No data storage:** client inputs and proposals are never saved; everything is wiped on refresh (no history)
- Dark, modern UI theme

## Prerequisites

- Python 3.12+
- An [OpenRouter API key](https://openrouter.ai/keys)

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
export OPENROUTER_API_KEY="sk-or-v1-..."
# OPTIONAL overrides:
# export OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
# export MODELS="anthropic/claude-3.5-sonnet,openai/gpt-4o-mini,meta-llama/llama-3.1-70b-instruct"

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

- Requires an internet connection to reach the configured API endpoint.
- The API key is read from `OPENROUTER_API_KEY` (env var or Streamlit secret) only; it is never stored on disk.
- If `MODELS` is not set, the pre-populated dropdown shows a curated default set (Claude 3.5 Sonnet, GPT-4o mini, Llama 3.1 70B).