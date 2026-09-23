# ⚡ AI Proposal & RFP Engine

A Streamlit app that converts raw client RFPs and emails into high-converting enterprise proposals using any OpenRouter AI model (Claude, GPT, Llama). Includes a built-in "WordSpinner" humanizer to rewrite AI-sounding text into a natural enterprise tone.

## Features

- Paste any client RFP / email and generate a complete enterprise proposal
- Choose from multiple AI engines via [OpenRouter](https://openrouter.ai)
- Configurable company portfolio & strengths context
- Humanizer toggle with adjustable intensity (Standard B2B, Conversational Enterprise, Ultra-Natural)
- Download the generated proposal as a `.txt` file

## Prerequisites

- Python 3.12+
- An [OpenRouter API key](https://openrouter.ai/keys)

## Setup & Run

```bash
# 1. Clone or navigate into the project
cd ai-proposal-generator

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

1. Enter your **OpenRouter API key** in the sidebar.
2. Pick an AI engine and configure the WordSpinner humanizer settings.
3. Review/update the company context in the sidebar.
4. In the main panel, enter the client name, paste the RFP/requirements, and select the core capabilities.
5. Click **🚀 Generate Enterprise Proposal** — the proposal appears on the right and can be downloaded as `.txt`.

## Project Structure

```
ai-proposal-generator/
├── main.py          # Streamlit app entry point
├── env/             # Local Python virtual environment (not required to commit)
└── README.md
```

## Notes

- Requires an internet connection to reach the OpenRouter API.
- The API key is entered at runtime in the UI only; it is never stored on disk.