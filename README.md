# DataMind AI

**DataMind AI** is an intelligent data analytics and document question-answering platform that leverages **Agentic AI**, **Retrieval-Augmented Generation (RAG)**, and **Large Language Models (LLMs)** to simplify data exploration through natural language. The system enables users to upload structured CSV datasets or PDF documents and interact with them conversationally, eliminating the need for complex SQL queries, manual analysis, or extensive document searching.

Built using **LangGraph**, **LangChain**, **Google Gemini 2.5 Flash**, **FAISS**, and **Streamlit**, DataMind AI intelligently routes user requests to the appropriate analytical workflow, providing accurate insights, visualizations, and context-aware responses.

---

## Key Features

| Feature | Description |
|---------|-------------|
| Conversational Data Analysis | Analyze CSV datasets using natural language queries. |
| PDF Question Answering | Retrieve contextual answers from uploaded PDF documents using RAG. |
| Intelligent Agent Routing | LangGraph dynamically selects the appropriate analytical tool based on user intent. |
| Automated Visualizations | Generate charts and graphs directly from user queries. |
| Statistical Analysis | Perform descriptive statistics, filtering, aggregation, and correlation analysis. |
| Semantic Search | Retrieve relevant document sections using vector embeddings and similarity search. |
| Interactive Web Interface | User-friendly Streamlit application for seamless interaction. |

---

# System Architecture

```
                    User
                      │
                      ▼
           Natural Language Query
                      │
                      ▼
              LangGraph Agent
                      │
      ┌───────────────┴────────────────┐
      │                                │
      ▼                                ▼
 CSV Analysis Pipeline          RAG Pipeline
 (Pandas & Plotly)        (Embeddings + FAISS)
      │                                │
      └───────────────┬────────────────┘
                      ▼
           Google Gemini 2.5 Flash
                      │
                      ▼
          Analytical Response / Charts
```

---

# Technology Stack

| Category | Technologies |
|----------|--------------|
| Programming Language | Python |
| Frontend | Streamlit |
| Agent Framework | LangGraph |
| LLM Framework | LangChain |
| Large Language Model | Google Gemini 2.5 Flash |
| Data Analysis | Pandas, NumPy |
| Visualization | Plotly, Matplotlib |
| Document Processing | PyPDF2 |
| Embeddings | Google Generative AI Embeddings |
| Vector Database | FAISS |
| Environment Management | Python Virtual Environment |

---

# Project Structure

```
DataMind-AI/
│
├── app.py
├── requirements.txt
├── README.md
├── .env
│
├── agent/
│   ├── graph.py
│   ├── router.py
│   └── tools.py
│
├── analytics/
│   ├── csv_analyzer.py
│   ├── visualization.py
│   └── statistics.py
│
├── rag/
│   ├── embeddings.py
│   ├── retriever.py
│   └── vector_store.py
│
├── uploads/
├── assets/
└── docs/
```

---

# Installation

### Clone the repository

```bash
git clone https://github.com/<username>/DataMind-AI.git
cd DataMind-AI
```

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root and add your Google Gemini API key.

```env
GOOGLE_API_KEY=YOUR_API_KEY
```

---

# Running the Application

Launch the Streamlit application using:

```bash
streamlit run app.py
```

The application will be available at:

```
http://localhost:8501
```

---

## Best Practices

- Use clean and well-structured datasets.
- Ensure column names are meaningful.
- Remove unnecessary columns before uploading.
- Use UTF-8 encoded CSV files for best compatibility.

# Usage

### CSV Analytics

Upload a CSV dataset and ask questions such as:

- Show summary statistics.
- Which product generated the highest revenue?
- Display monthly sales trends.
- Find correlations between variables.
- Show the top 10 performing records.

### PDF Question Answering

Upload a PDF document and ask:

- Summarize the document.
- What are the key findings?
- Explain the methodology.
- What conclusions were drawn?
- Extract important information from Chapter 3.

---

# Workflow

1. The user uploads a CSV file or PDF document.
2. A natural language query is submitted through the interface.
3. The LangGraph agent identifies the user's intent.
4. Based on the query, the agent routes the request to either:
   - CSV Analysis Pipeline
   - Retrieval-Augmented Generation (RAG) Pipeline
5. The selected pipeline processes the request.
6. Google Gemini generates a contextual response, while charts or statistical summaries are produced when required.

---

# Evaluation Summary

| Metric | Performance |
|---------|------------:|
| CSV Analysis Accuracy | 85% |
| Tool Selection Accuracy | 90% |
| Chart Generation Success | 80% |
| Average Response Time | 8–10 seconds |

---

# Future Enhancements

- Multi-document Retrieval-Augmented Generation
- SQL Database Integration
- Voice-based Natural Language Interface
- Advanced Dashboard Generation
- User Authentication and Role Management
- Cloud Deployment
- Persistent Agent Memory
- Exportable Reports (PDF/Excel)

---

# Screenshots

The following screenshots can be added after deployment:

- Home Page
- CSV Upload Interface
- PDF Upload Interface
- Data Analysis Results
- Chart Generation
- Document Question Answering

---

# References

- LangChain
- LangGraph
- Google Gemini API
- Streamlit
- FAISS
- Pandas
- Plotly
- PyPDF2

---

# Team Members

| Name |
|------|
| **Diya Khampa** |
| **Aanchal Tanwar** |
| **Diya Gupta** |
| **Kanika Goyal** |

---

# License

This project was developed as part of an academic Software Innovation Project (SIP) and is intended for educational and research purposes.
