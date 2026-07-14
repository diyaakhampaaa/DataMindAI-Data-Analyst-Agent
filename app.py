"""
P4 owns this file — Integration & Presentation Lead.

This is the only file that touches Streamlit. It never calls P1 or
P3's code directly — it only talks to AgentSession (P2's interface),
which is the contract the whole team agreed on.
"""
import os
import streamlit as st
from dotenv import load_dotenv

from agent.agent import AgentSession
from tools.data_tools import load_csv, clean_data
from tools.rag_tools import extract_and_chunk, embed_and_store

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "")

st.set_page_config(page_title="DataMind AI", page_icon="📊", layout="wide")
st.title("📊 DataMind AI — Conversational Data Analyst")
st.caption("Upload a CSV and/or a PDF, then ask questions in plain English.")

if not API_KEY:
    st.error("GEMINI_API_KEY not set. Add it to a .env file in the project root.")
    st.stop()

# --- session state setup ---
if "session" not in st.session_state:
    st.session_state.session = AgentSession(api_key=API_KEY)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of (role, content)
if "csv_loaded" not in st.session_state:
    st.session_state.csv_loaded = False
if "pdf_loaded" not in st.session_state:
    st.session_state.pdf_loaded = False

session = st.session_state.session

# --- sidebar: uploads ---
with st.sidebar:
    st.header("Upload data")

    csv_file = st.file_uploader("Upload CSV", type=["csv"])
    if csv_file is not None and not st.session_state.csv_loaded:
        with st.spinner("Loading and cleaning CSV..."):
            df = clean_data(load_csv(csv_file))
            session.df = df
            st.session_state.csv_loaded = True
        st.success(f"CSV loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        st.dataframe(df.head(3))

    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
    if pdf_file is not None and not st.session_state.pdf_loaded:
        with st.spinner("Extracting, chunking, and embedding PDF..."):
            temp_path = f"/tmp/{pdf_file.name}"
            with open(temp_path, "wb") as f:
                f.write(pdf_file.getbuffer())

            doc_id = pdf_file.name.replace(" ", "_").replace(".pdf", "")
            chunks = extract_and_chunk(temp_path)
            embed_and_store(chunks, doc_id, API_KEY)

            session.doc_id = doc_id
            st.session_state.pdf_loaded = True
        st.success(f"PDF processed: {len(chunks)} chunks indexed")

    if st.button("Reset session"):
        st.session_state.clear()
        st.rerun()

# --- main chat area ---
for role, content in st.session_state.chat_history:
    with st.chat_message(role):
        st.write(content)

user_input = st.chat_input("Ask a question about your data or document...")

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response, chart_path = session.ask(user_input, st.session_state.chat_history[:-1])
            st.write(response)
            if chart_path and os.path.exists(chart_path):
                st.image(chart_path)

    st.session_state.chat_history.append(("assistant", response))
