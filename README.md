# DataMind AI

Conversational data analyst agent — ask questions about an uploaded CSV
(stats, filters, group-bys, charts) or an uploaded PDF (RAG-based Q&A
with page citations) in plain English.

## Everyone — do this first

```bash
git clone <repo-url>
cd datamind-ai
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# then paste your Gemini API key into .env
```
Run the app once everything below is wired up:
```bash
streamlit run app.py
```

## Who owns what

| File | Owner | Role |
|---|---|---|
| `tools/data_tools.py` | P1 | CSV loading, cleaning, 6 analysis functions |
| `agent/agent.py`, `agent/prompts.py` | P2 | LangGraph agent, tool routing, memory |
| `tools/rag_tools.py` | P3 | PDF parsing, chunking, embeddings, retrieval |
| `app.py` | P4 | Streamlit UI, integration, demo |

## The interface contract (don't break this)

- P1's functions take `(df, **kwargs)` and return a result (DataFrame, dict, or chart path)
- P3's `rag_query(query, doc_id, api_key)` returns a string answer with page citations
- P2's `AgentSession.ask(user_message, chat_history)` returns `(response_text, chart_path_or_none)`
- P4 (`app.py`) only ever calls `AgentSession` — never touches `data_tools` or `rag_tools` directly

This is what lets all four of us work in parallel without blocking
on each other. If you need to change a function signature, message
the team before you do it — it breaks someone else's code silently otherwise.

## Testing your piece independently

**P1** — test `tools/data_tools.py` directly against `data/sample_employees.csv`:
```bash
python3 -c "
from tools.data_tools import load_csv, clean_data, get_stats
df = clean_data(load_csv('data/sample_employees.csv'))
print(get_stats(df, 'salary'))
"
```

**P3** — test extraction/chunking without needing the API key first:
```bash
python3 -c "
from tools.rag_tools import extract_and_chunk
chunks = extract_and_chunk('data/sample_paper.pdf')
print(len(chunks), 'chunks extracted')
"
```
Then test the full pipeline (needs API key in `.env`):
```bash
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
from tools.rag_tools import extract_and_chunk, embed_and_store, rag_query
chunks = extract_and_chunk('data/sample_paper.pdf')
embed_and_store(chunks, 'test_doc', os.getenv('GEMINI_API_KEY'))
print(rag_query('What is this document about?', 'test_doc', os.getenv('GEMINI_API_KEY')))
"
```

**P2** — test the agent directly once P1 and P3 have working functions:
```bash
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
from agent.agent import AgentSession
from tools.data_tools import load_csv, clean_data

session = AgentSession(api_key=os.getenv('GEMINI_API_KEY'))
session.df = clean_data(load_csv('data/sample_employees.csv'))
response, chart = session.ask('What is the average salary?', [])
print(response)
"
```

**P4** — once P1/P2/P3 have working code, just run:
```bash
streamlit run app.py
```

## Architecture

```
User question (Streamlit chat)
        │
        ▼
AgentSession.ask()  [P2 — LangGraph ReAct agent]
        │
        ├── stats_tool, filter_tool, group_by_tool,
        │   top_n_tool, correlate_tool, chart_tool  ──►  tools/data_tools.py [P1]
        │
        └── document_qa_tool  ──►  tools/rag_tools.py [P3]
                                        │
                                        ▼
                              ChromaDB (chroma_db/) — per-document collections
```

## known limitations (be upfront about these in the report/demo)

- Embeddings are generated one chunk at a time in a loop — fine for
  capstone-scale PDFs, would need batching for large-scale production use
- Chat memory is passed as raw message history each turn, not
  summarized — long conversations will eventually hit context limits
- No authentication / multi-user isolation — single-session, single-user by design
