import streamlit as st

from config import get_settings
from errors import ProposalGenerationError
from prompts import HUMANIZATION_LEVELS
from proposal_pipeline import generate_proposal_artifact


def main() -> None:
    settings = get_settings()
    st.set_page_config(
        page_title="AI Proposal & RFP Engine",
        layout="wide",
        page_icon="⚡",
        menu_items={"Get help": None, "Report a bug": None, "About": None},
    )

    st.markdown(
        """
        <style>
        .main { background-color: #0f172a; color: #f8fafc; }

        /* White-label: hide all Streamlit branding & chrome */
        #MainMenu, [data-testid="stMainMenu"] { visibility: hidden; }
        footer { visibility: hidden; }
        [data-testid="stHeader"] { display: none !important; }
        [data-testid="stToolbar"] { display: none !important; }
        [data-testid="stFooter"] { display: none !important; }
        [data-testid="stAppDeployButton"], [data-testid="stStatusWidget"] { display: none !important; }
        header[data-testid="stHeader"] .decoration { display: none !important; }
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
        """,
        unsafe_allow_html=True,
    )

    st.title("⚡ AI Proposal & RFP Engine")
    st.caption("Convert Raw Client RFPs into High-Converting Enterprise Proposals.")

    st.info(
        "🔒 **Privacy Notice:** Your client inputs and generated proposals are **not saved anywhere**. "
        "Everything lives only in this browser session and **will be wiped on refresh** — there is **no history**. "
        "**Copy or download your proposal as a `.docx` file** before refreshing the page."
    )

    api_key = settings.api_key
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("OPENROUTER_API_KEY")
        except Exception:
            api_key = None
    base_url = settings.base_url

    st.sidebar.header("⚙️ Configuration")
    model_choice = st.sidebar.selectbox("Choose AI Engine", list(settings.models))

    if not api_key:
        api_key = st.sidebar.text_input(
            "API key (session only)",
            type="password",
            help="Used for this browser session only; it is not written to disk.",
        ).strip()
    if not api_key:
        st.error(
            "❌ Missing API key. Set it in `.env`, a Streamlit secret, or the session-only field."
        )
        st.stop()

    st.sidebar.markdown("---")
    st.sidebar.subheader("✍️ WordSpinner Settings")
    enable_humanizer = st.sidebar.toggle("Enable Humanized Natural Tone", value=True)
    humanize_level = st.sidebar.select_slider(
        "Humanization Intensity",
        options=list(HUMANIZATION_LEVELS),
        value="Conversational Enterprise",
    )

    company_context = st.sidebar.text_area(
        "Company Portfolio & Strengths",
        value=settings.company_context,
        height=120,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Input Client Requirements")
        client_name = st.text_input("Client Company Name", value="Apex Logistics Global")
        rfp_text = st.text_area(
            "Paste RFP / Client Email Here",
            height=280,
            placeholder="Paste client requirements here...",
        )

        tech_stack = st.multiselect(
            "Select Core Focus Capabilities",
            [
                "Agentic AI / LLMs",
                "Verifiable Data Governance & Security",
                "System Integration (SAP/Oracle)",
                "Cloud & Enterprise Architecture",
            ],
            default=[
                "Agentic AI / LLMs",
                "Verifiable Data Governance & Security",
            ],
        )

        generate_btn = st.button(
            "🚀 Generate Enterprise Proposal", use_container_width=True
        )

    with col2:
        st.subheader("2. Generated Proposal Output")
        if generate_btn:
            if not rfp_text:
                st.warning("Please paste client requirements first.")
            else:
                with st.spinner(
                    "Step 1: Analyzing RFP & Building Proposal Architecture..."
                ):
                    try:
                        artifact = generate_proposal_artifact(
                            api_key=api_key,
                            base_url=base_url,
                            model=model_choice,
                            company_context=company_context,
                            client_name=client_name,
                            capabilities=tech_stack,
                            rfp_text=rfp_text,
                            humanize_level=humanize_level,
                            enable_humanizer=enable_humanizer,
                        )
                        proposal = artifact.proposal
                        proposal_output = artifact.text
                        spinner_result = artifact.spinner_result

                        if spinner_result is not None:
                            if spinner_result.hits:
                                st.warning(
                                    f"WordSpinner flagged {spinner_result.hit_count} buzzword "
                                    "occurrence(s). Review the before/after pass below."
                                )
                                st.dataframe(
                                    [
                                        {
                                            "term": hit.term,
                                            "matched_text": hit.matched_text,
                                            "location": hit.location,
                                            "sentence": hit.sentence,
                                        }
                                        for hit in spinner_result.hits
                                    ],
                                    hide_index=True,
                                    use_container_width=True,
                                )
                                with st.expander(
                                    "WordSpinner before/after review", expanded=True
                                ):
                                    st.code(spinner_result.review, language="diff")
                            else:
                                st.success("WordSpinner found no dictionary buzzwords.")

                        st.success("Proposal generated successfully!")
                        with st.expander(
                            "Structured proposal fields", expanded=False
                        ):
                            st.json(proposal.to_dict())
                        st.text_area(
                            "Final Proposal (Copy/Edit)",
                            value=proposal_output,
                            height=420,
                        )

                        st.download_button(
                            label="📥 Download Proposal (.docx)",
                            data=artifact.docx_data,
                            file_name=f"Proposal_{client_name.replace(' ', '_')}.docx",
                            mime=(
                                "application/vnd.openxmlformats-officedocument."
                                "wordprocessingml.document"
                            ),
                        )
                    except ProposalGenerationError as error:
                        st.error(error.user_message)
                    except Exception:
                        st.error(
                            "An unexpected error occurred while preparing the proposal. "
                            "Check the provider settings and try again."
                        )


if __name__ == "__main__":
    main()
