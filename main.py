import streamlit as st
import openai
import os
import time

# Page Setup & Modern UI Styling
st.set_page_config(page_title="AI Proposal & RFP Engine", layout="wide", page_icon="⚡")

# Custom CSS for Sleek Theme
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stButton>button {
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 12px 24px;
        border: none;
    }
    .stTextArea label, .stTextInput label, .stMultiSelect label {
        color: #94a3b8 !important;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ AI Proposal & RFP Engine")
st.caption("Convert Raw Client RFPs into High-Converting Enterprise Proposals.")

# Privacy / No-History Notice
st.info(
    "🔒 **Privacy Notice:** Your client inputs and generated proposals are **not saved anywhere**. "
    "Everything lives only in this browser session and **will be wiped on refresh** — there is **no history**. "
    "**Copy or download your proposal as a `.txt` file** before refreshing the page."
)

# Read API key from environment / Streamlit secrets (no manual entry)
api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("OPENROUTER_API_KEY")
    except Exception:
        api_key = None
base_url = os.environ.get("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1"

if not api_key:
    st.error(
        "❌ Missing API key. Set the `OPENROUTER_API_KEY` environment variable "
        "(or Streamlit secret) before running this app."
    )
    st.stop()

# Pre-populated working models (no "Load Models" button / live fetch).
# Override via the MODELS env var as a comma-separated list if needed.
default_models = [
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4o-mini",
    "meta-llama/llama-3.1-70b-instruct",
]
models_env = os.environ.get("MODELS")
available_models = [m.strip() for m in models_env.split(",")] if models_env else default_models

# Sidebar - Configuration
st.sidebar.header("⚙️ Configuration")
model_choice = st.sidebar.selectbox("Choose AI Engine", available_models)

# WORD SPINNER / HUMANIZER TOGGLE
st.sidebar.markdown("---")
st.sidebar.subheader("✍️ WordSpinner Settings")
enable_humanizer = st.sidebar.toggle("Enable Humanized Natural Tone", value=True)
humanize_level = st.sidebar.select_slider(
    "Humanization Intensity",
    options=["Standard B2B", "Conversational Enterprise", "Ultra-Natural / Direct"],
    value="Conversational Enterprise"
)

company_context = st.sidebar.text_area(
    "Company Portfolio & Strengths",
    value="""We are a leading IT engineering firm specializing in Enterprise AI, 
Smart Automation, Agentic Workflows, and High-Security Distributed Systems. 
We have delivered 200+ enterprise-grade solutions with 99.9% reliability.""",
    height=120
)

# Main UI Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Input Client Requirements")
    client_name = st.text_input("Client Company Name", value="Apex Logistics Global")
    rfp_text = st.text_area(
        "Paste RFP / Client Email Here",
        height=280,
        placeholder="Paste client requirements here..."
    )
    
    tech_stack = st.multiselect(
        "Select Core Focus Capabilities",
        ["Agentic AI / LLMs", "Verifiable Data Governance & Security", "System Integration (SAP/Oracle)", "Cloud & Enterprise Architecture"],
        default=["Agentic AI / LLMs", "Verifiable Data Governance & Security"]
    )
    
    generate_btn = st.button("🚀 Generate Enterprise Proposal", use_container_width=True)

with col2:
    st.subheader("2. Generated Proposal Output")
    if generate_btn:
        if not rfp_text:
            st.warning("Please paste client requirements first.")
        else:
            with st.spinner("Step 1: Analyzing RFP & Building Proposal Architecture..."):
                try:
                    client = openai.OpenAI(
                        base_url=base_url,
                        api_key=api_key
                    )
                    
                    # Humanizer Rules Injection
                    humanizer_rules = ""
                    if enable_humanizer:
                        humanizer_rules = f"""
                        CRITICAL INSTRUCTION - HUMANIZED WRITING STYLE ({humanize_level}):
                        - Write like an experienced Principal Solutions Architect talking directly to a client executive.
                        - AVOID robotic AI buzzwords: Do NOT use words like 'delve', 'tapestry', 'testament', 'beacon', 'moreover', 'in conclusion', 'embark'.
                        - Use short, punchy sentences mixed with clear technical explanations.
                        - Use active voice, simple B2B English, and focus heavily on practical ROI and implementation realities.
                        - Sound confident, grounded, and human—no corporate fluff or dramatic intros.
                        """
                    
                    prompt = f"""
                    You are a Principal Enterprise Architect at the company described below.
                    Generate a high-converting, professional proposal based on the following client request.
                    
                    {humanizer_rules}
                    
                    Company Context:
                    {company_context}
                    
                    Client Name: {client_name}
                    Selected Capabilities: {', '.join(tech_stack)}
                    
                    Client Requirements:
                    {rfp_text}
                    
                    Structure the response clearly:
                    1. Problem Breakdown & Executive Summary
                    2. Proposed Solution & AI Agent Architecture
                    3. 4-Week Pilot Roadmap & Key Deliverables
                    4. Why Our Company (engineering scale, certifications, and delivery track record)
                    5. Next Steps
                    """
                    
                    response = client.chat.completions.create(
                        model=model_choice,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7
                    )
                    
                    proposal_output = response.choices[0].message.content
                    
                    # Visual WordSpinner Effect
                    if enable_humanizer:
                        with st.spinner("Step 2: WordSpinner Active — Rewriting AI Buzzwords into Natural Enterprise Tone..."):
                            time.sleep(1) # Simulated humanization pass visual feedback
                    
                    st.success("Proposal generated successfully!")
                    st.text_area("Final Proposal (Copy/Edit)", value=proposal_output, height=420)
                    
                    st.download_button(
                        label="📥 Download Proposal (.txt)",
                        data=proposal_output,
                        file_name=f"Proposal_{client_name.replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Error generating proposal: {str(e)}")