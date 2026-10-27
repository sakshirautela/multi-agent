import os
import streamlit as st
from datetime import datetime
from src.config import config, Config
from src.graph import research_graph

st.set_page_config(
    page_title="Multi-Agent AI Research Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished interface
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-success { background-color: #DCFCE7; color: #166534; }
    .badge-warning { background-color: #FEF3C7; color: #92400E; }
    .source-card {
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        margin-bottom: 10px;
        background-color: #F8FAFC;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Assistant Settings")
    st.markdown("Configure agent parameters and credentials.")

    provider_choice = st.radio(
        "LLM Provider",
        options=["Google Gemini", "OpenAI"],
        index=0 if config.active_provider != "openai" else 1
    )
    selected_provider = "openai" if provider_choice == "OpenAI" else "gemini"
    config.llm_provider = selected_provider

    if selected_provider == "gemini":
        gemini_key = st.text_input(
            "Google Gemini API Key",
            value=config.gemini_api_key,
            type="password",
            help="Get your key at https://aistudio.google.com/"
        )
        if gemini_key:
            os.environ["GEMINI_API_KEY"] = gemini_key
            config.gemini_api_key = gemini_key

        model_choice = st.selectbox(
            "Gemini Model",
            options=["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
            index=0
        )
        config.gemini_model = model_choice
    else:
        openai_key = st.text_input(
            "OpenAI API Key",
            value=config.openai_api_key,
            type="password",
            help="Get your key at https://platform.openai.com/api-keys"
        )
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
            config.openai_api_key = openai_key

        openai_model_choice = st.selectbox(
            "OpenAI Model",
            options=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "o3-mini"],
            index=0
        )
        config.openai_model = openai_model_choice

    tavily_key = st.text_input(
        "Tavily Search API Key",
        value=config.tavily_api_key,
        type="password",
        help="Optional: If blank, system automatically uses DuckDuckGo!"
    )
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key
        config.tavily_api_key = tavily_key

    max_loops = st.slider("Max Gap-Filling Loops", min_value=1, max_value=3, value=config.max_research_loops)
    config.max_research_loops = max_loops

    st.markdown("---")
    st.markdown("### 🤖 Active Agent Fleet")
    st.markdown("""
    - **Orchestrator**: Sub-question decomposition
    - **Researcher**: Multi-engine retrieval & dedup
    - **Analyst**: Evidence extraction & cross-check
    - **Report Writer**: Citation-grounded synthesis
    - **Validator**: Hallucination & link audit
    """)

# Main Content
st.markdown('<div class="main-header">Multi-Agent AI Research Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Collaborative agent swarm: autonomous web research, cross-source evidence verification, and cited synthesis.</div>', unsafe_allow_html=True)

# Search Input
default_query = "Latest developments in Multi-Agent AI Architectures and LangGraph"
research_topic = st.text_input("Enter Research Question or Topic:", value=default_query)

col_run, col_clear = st.columns([1, 5])
with col_run:
    start_btn = st.button("🚀 Start Research", type="primary", use_container_width=True)

if start_btn and research_topic.strip():
    initial_state = {
        "topic": research_topic.strip(),
        "sub_questions": [],
        "search_queries": [],
        "sources": {},
        "analysis": {},
        "loop_count": 0,
        "max_loops": config.max_research_loops,
        "report_markdown": "",
        "validation": {},
        "status_logs": []
    }

    progress_placeholder = st.empty()
    status_box = st.status("Initializing research agents...", expanded=True)

    final_state = initial_state
    try:
        for output in research_graph.stream(initial_state):
            for node_name, node_state in output.items():
                logs = node_state.get("status_logs", [])
                latest_msg = logs[-1]["message"] if logs else f"Executing {node_name}..."
                status_box.write(f"**[{node_name.capitalize()}]**: {latest_msg}")
                final_state.update(node_state)

        status_box.update(label="✅ Research Pipeline Completed!", state="complete", expanded=False)
        st.session_state["research_result"] = final_state

    except Exception as e:
        status_box.update(label=f"❌ Error during workflow execution: {e}", state="error")
        st.error(f"Execution failed: {e}")

# Display Results if available
if "research_result" in st.session_state:
    res = st.session_state["research_result"]
    report_md = res.get("report_markdown", "")
    sources = res.get("sources", {})
    analysis = res.get("analysis", {})
    validation = res.get("validation", {})
    claims = analysis.get("claims", [])

    st.markdown("---")

    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Sources Retrieved", len(sources))
    m2.metric("Verified Claims", len(claims))
    m3.metric("Research Rounds", res.get("loop_count", 0) + 1)
    passed = validation.get("passed", False)
    m4.metric("Citation Audit", "Passed (100%)" if passed else "Flagged Warnings")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Research Report",
        "🔍 Evidence & Claims Matrix",
        "🌐 Source Registry",
        "🛡️ Citation Audit"
    ])

    with tab1:
        st.download_button(
            label="📥 Download Report (.md)",
            data=report_md,
            file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
        st.markdown(report_md)

    with tab2:
        st.subheader("Extracted Factual Claims & Cross-Source Verification")
        if claims:
            for idx, c in enumerate(claims, 1):
                cat_badge = c.get('category', 'fact').upper()
                st.markdown(f"""
                <div class="source-card">
                    <b>Claim #{idx}</b>: {c.get('claim')}<br/>
                    <small><b>Source Reference:</b> <code>[{c.get('source_id')}]</code> | <b>Type:</b> {cat_badge} | <b>Confidence:</b> {c.get('confidence', 'high')}</small><br/>
                    <i>Evidence Quote:</i> "{c.get('evidence_quote')}"
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No claims extracted.")

        contradictions = analysis.get("contradictions", [])
        if contradictions:
            st.warning("⚠️ **Conflicting Evidence Identified Between Sources:**")
            for c in contradictions:
                st.markdown(f"- {c}")

        gaps = analysis.get("gaps", [])
        if gaps:
            st.info("ℹ️ **Information Gaps Addressed:**")
            for g in gaps:
                st.markdown(f"- {g}")

    with tab3:
        st.subheader("Indexed Source Cards")
        if sources:
            for sid, sdata in sources.items():
                st.markdown(f"""
                <div class="source-card">
                    <b>[{sid}] {sdata.get('title', 'Untitled')}</b><br/>
                    <a href="{sdata.get('url', '#')}" target="_blank">{sdata.get('url', '')}</a><br/>
                    <small>Domain: <code>{sdata.get('domain', '')}</code></small>
                    <p style="margin-top: 6px; font-size: 0.9rem; color: #334155;">{sdata.get('snippet', '')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No sources registered.")

    with tab4:
        st.subheader("Citation Integrity & Audit Details")
        st.json(validation)
