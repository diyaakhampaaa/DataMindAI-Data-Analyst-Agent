# DataMind AI

**DataMind AI** is a conversational data analyst agent that lets you ask questions about a CSV dataset or a PDF document in plain English — no SQL, no manual digging through spreadsheets or pages. Built as our capstone for the IGDTUW × Sansoftech Generative & Agentic AI Systems Development internship (SIP 2026).

**Live demo:** [https://datamindai-data-analyst-agent-vv2p3rutdftcgbsxjbxrdn.streamlit.app/](https://datamindai-data-analyst-agent-vv2p3rutdftcgbsxjbxrdn.streamlit.app/) 
---

## What it does

Upload a CSV and ask things like *"what's the average salary by department?"* or *"show me a bar chart of sales by region"* — the agent computes real answers from your data and generates charts on request.

Upload a PDF and ask things like *"what does this paper say about X?"* — the agent retrieves the relevant passages and answers grounded in the actual document, citing which page the answer came from.

A single LangGraph agent handles both — it decides which tool to call based on what you're asking, so you can work with a dataset and a document in the same conversation.

---

## Architecture

```text
                           User
                             │
                             ▼
                 Natural Language Query
                             │
                             ▼
                      LangGraph Agent
                             │
               ┌─────────────┴─────────────┐
               │                           │
               ▼                           ▼
     CSV Analysis Pipeline           RAG Pipeline
      (Pandas + Plotly)        (Embeddings + FAISS)
               │                           │
               └─────────────┬─────────────┘
                             │
                             ▼
                  Google Gemini 2.5 Flash
                             │
                             ▼
                Analytical Response / Charts
```

The agent always calls a tool to get real numbers or real document text rather than generating answers from memory — this is the core mitigation for hallucination risk in the project.

---

## Tech stack

| Category | Technology |
|---|---|
| Agent framework | LangGraph + LangChain |
| LLM | Google Gemini (`gemini-flash-latest`) |
| Embeddings | Google Gemini (`gemini-embedding-001`) |
| Vector store | ChromaDB |
| Data analysis | Pandas, NumPy |
| Visualization | Matplotlib |
| PDF parsing | pypdf |
| Frontend | Streamlit |
| Deployment | Streamlit Community Cloud |

---
## Project Structure
``` text
.
├── .streamlit/
│   └── config.toml
├── agent/
│   ├── __init__.py
│   ├── agent.py
│   └── prompts.py
├── tools/
│   ├── __init__.py
│   ├── data_tools.py
│   └── rag_tools.py
├── data/
│   ├── sample_employees.csv
│   └── sample_paper.pdf
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```
---

## Running it locally

```bash
git clone https://github.com/diyaakhampaaa/DataMindAI-Data-Analyst-Agent.git

cd DataMindAI-Data-Analyst-Agent

python -m venv venv

venv\Scripts\activate        # macOS/Linux: source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env         # then add your Gemini API key

streamlit run app.py
```

Get a free Gemini API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

> **Free tier limits:** ~5 requests/minute and a small daily cap per key. If you hit a `429 RESOURCE_EXHAUSTED` error, wait a minute — it's a rate limit, not a bug.

---

## Key design decisions

- **Tool-grounded answers, not free generation** — every numeric answer and every document answer comes from an actual Pandas computation or retrieved PDF chunk, not the model's guess. This directly addresses hallucination risk.
- **Page-cited RAG** — PDF chunks retain their source page number from extraction through to the final answer, so document answers can cite exactly where they came from.
- **Single hybrid agent** — rather than separate CSV and PDF tools with no shared interface, one LangGraph agent routes between both based on the question, so a single conversation can span both data types.

---

## Known limitations

- Embeddings are generated one chunk at a time — fine at capstone scale, would need batching for large documents
- Chat memory is raw message history, not summarized — long conversations will eventually hit context limits
- No authentication or multi-user isolation — single-session by design
- Free-tier API rate limits constrain concurrent usage during demos

---

## Future enhancements

- Multi-document RAG (query across several PDFs at once)
- SQL database integration alongside CSV upload
- Persistent chat memory across sessions
- Exportable reports (PDF/Excel)

---

## Team

| Name | 
|---|
| Diya Khampa |
| Aanchal Tanwar |
| Diya Gupta |
| Kanika Goyal | 

---

## Acknowledgements

Built as part of the **Generative & Agentic AI Systems Development** Summer Internship Program 2026, IGDTUW Department of IT in collaboration with Sansoftech Services.

---

