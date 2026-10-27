# Multi-Agent AI Research Assistant

An autonomous multi-agent research swarm built using **LangGraph**, **Google Gemini**, **Tavily Search**, and **Python**.

---

## 🏗️ Architecture & Agent Fleet

```
                        [ User Research Query ]
                                   │
                                   ▼
                       [ Orchestrator Agent ]
                   (Decomposition & Search Planning)
                                   │
                                   ▼
                       [ Researcher Agent ]
             (Multi-Engine Search, Dedup & Source Cards)
                                   │
                                   ▼
                         [ Analyst Agent ]
            (Factual Claims, Contradiction & Gap Detection)
                                   │
                     ┌─────────────┴─────────────┐
                     ▼                           ▼
            [ Gaps Found? ]             [ Evidence Complete ]
            (Loop < Max Loops)                   │
                     │                           ▼
                     └──► Re-search     [ Report Writer Agent ]
                                     (Cited Synthesis with [S#])
                                                 │
                                                 ▼
                                        [ Validator Agent ]
                                     (Citation Integrity Audit)
                                                 │
                                                 ▼
                                     [ Final Research Report ]
```

### Specialized Agents:
1. **Orchestrator**: Breaks down the topic into 3–4 sub-questions and high-yield search queries.
2. **Researcher**: Executes searches across Tavily (with automatic DuckDuckGo fallback), deduplicates domains/URLs, cleans raw content, and assigns unique source identifiers (`S1`, `S2`, ...).
3. **Analyst**: Examines retrieved evidence, isolates factual claims with direct quotation evidence, surfaces conflicting viewpoints, and triggers re-search loops if gaps remain.
4. **Report Writer**: Synthesizes structured markdown briefings where every factual claim is anchored by citations (e.g., `[S1]`, `[S2]`).
5. **Validator**: Audits the generated report to verify 100% citation grounding against real sources and eliminate hallucinated references.

---

## 🚀 Getting Started

### 1. Environment Setup

The virtual environment `.venv` is ready. To activate it manually:
```bash
source .venv/bin/activate
```

Dependencies installed:
- `langgraph`
- `openai`
- `google-genai`
- `langchain-google-genai`
- `tavily-python`
- `ddgs` (DuckDuckGo Search)
- `streamlit`
- `rich`
- `pydantic`

### 2. Configure API Keys

Edit [.env](file:///Users/user/Desktop/sakshirautela/multi-agent/.env) (reference [.env.example](file:///Users/user/Desktop/sakshirautela/multi-agent/.env.example)):

```bash
# Choose default provider: "gemini" or "openai"
LLM_PROVIDER=gemini

# Google Gemini API Key (Get at https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# OpenAI API Key (Get at https://platform.openai.com/api-keys)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Tavily Search API Key (Optional: Falls back to DuckDuckGo if blank)
TAVILY_API_KEY=your_tavily_api_key_here

# Maximum gap-filling loops (default: 2)
MAX_RESEARCH_LOOPS=2
```

---

## 💻 Running the Assistant

### Option A: Command Line Interface (CLI)

Run research directly from the terminal with live agent logs and Rich formatting:

```bash
.venv/bin/python main.py "Latest breakthroughs in Agentic AI and Memory Systems"
```

Generated reports are automatically saved to the [reports/](file: ../multi-agent/reports) directory.

### Option B: Interactive Streamlit Web Interface

Launch the interactive UI:

```bash
.venv/bin/streamlit run app.py
```

Features:
- **Live agent workflow logs**: Watch each agent process in real-time.
- **Interactive Report**: View and download the finalized Markdown report.
- **Evidence Matrix**: Browse extracted claims, source citations, and confidence scores.
- **Source Registry**: Inspect original snippets, URLs, and domains.
- **Citation Audit**: Review hallucination checks and citation validation metrics.
