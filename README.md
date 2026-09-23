# ⚡ AI Proposal & RFP Engine

A Streamlit app that converts raw client RFPs and emails into high-converting enterprise proposals using any OpenAI-compatible AI model (Claude, GPT, Llama) via OpenRouter. Includes a built-in "WordSpinner" humanizer that rewrites AI-sounding text into a natural enterprise tone.

## Features

- Paste any client RFP / email and generate a complete enterprise proposal
- Live model list fetched from your API provider, or pick from built-in fallbacks
- Configurable API Base URL (works with OpenRouter or any OpenAI-compatible endpoint)
- Dynamic model loading with a single click
- Configurable company portfolio & strengths context
- WordSpinner humanizer toggle with adjustable intensity (Standard B2B, Conversational Enterprise, Ultra-Natural / Direct)
- Selectable core focus capabilities to steer the proposal
- Download the generated proposal as a `.txt` file
- Dark, modern UI theme

## Prerequisites

- Python 3.12+
- An [OpenRouter API key](https://openrouter.ai/keys)

## Setup & Run

```bash
# 1. Clone or navigate into the project
cd ProposalForge

# 2. Create a virtual environment
python3 -m venv env

# 3. Activate it
source env/bin/activate        # Linux / macOS
# .\env\Scripts\activate      # Windows (PowerShell)

# 4. Install dependencies
pip install streamlit openai

# 5. Launch the app
streamlit run main.py
```

That's it. Your browser will open automatically at `http://localhost:8501`.

## Usage

1. In the sidebar, enter your **API key** (leave the Base URL as the OpenRouter default unless you use a different provider).
2. Optionally click **🔄 Load Models** to fetch the live model list, then pick an AI engine.
3. Configure the **WordSpinner** humanizer settings and review/update the company context.
4. In the main panel, enter the client name, paste the RFP/requirements, select the core capabilities, and click **🚀 Generate Enterprise Proposal**.
5. The structured proposal appears on the right — copy it or download it as a `.txt` file.

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
├── main.py          # Streamlit app entry point
├── env/             # Local Python virtual environment (not required to commit)
└── README.md
```

## Notes

- Requires an internet connection to reach the configured API endpoint.
- The API key is entered at runtime in the UI only; it is never stored on disk.
- If the model list hasn't been loaded from the API, a set of fallback models (Claude, GPT-4o mini, Llama 3.1) is shown for selection.