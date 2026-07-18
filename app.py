# import os
# import streamlit as st
# from dotenv import load_dotenv

# from agent.agent import AgentSession
# from tools.data_tools import load_csv, clean_data
# from tools.rag_tools import extract_and_chunk, embed_and_store

# load_dotenv()
# API_KEY = os.getenv("GEMINI_API_KEY", "")

# st.set_page_config(page_title="DataMind AI", page_icon="📊", layout="wide")
# st.title("📊 DataMind AI — Conversational Data Analyst")
# st.caption("Upload a CSV and/or a PDF, then ask questions in plain English.")

# if not API_KEY:
#     st.error("GEMINI_API_KEY not set. Add it to a .env file in the project root.")
#     st.stop()

# # --- session state setup ---
# if "session" not in st.session_state:
#     st.session_state.session = AgentSession(api_key=API_KEY)
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []  # list of (role, content)
# if "csv_loaded" not in st.session_state:
#     st.session_state.csv_loaded = False
# if "pdf_loaded" not in st.session_state:
#     st.session_state.pdf_loaded = False

# session = st.session_state.session

# # --- sidebar: uploads ---
# with st.sidebar:
#     st.header("Upload data")

#     csv_file = st.file_uploader("Upload CSV", type=["csv"])
#     if csv_file is not None and not st.session_state.csv_loaded:
#         with st.spinner("Loading and cleaning CSV..."):
#             df = clean_data(load_csv(csv_file))
#             session.df = df
#             st.session_state.csv_loaded = True
#         st.success(f"CSV loaded: {df.shape[0]} rows, {df.shape[1]} columns")
#         st.dataframe(df.head(3))

#     pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
#     if pdf_file is not None and not st.session_state.pdf_loaded:
#         with st.spinner("Extracting, chunking, and embedding PDF..."):
#             temp_path = f"/tmp/{pdf_file.name}"
#             with open(temp_path, "wb") as f:
#                 f.write(pdf_file.getbuffer())

#             doc_id = pdf_file.name.replace(" ", "_").replace(".pdf", "")
#             chunks = extract_and_chunk(temp_path)
#             embed_and_store(chunks, doc_id, API_KEY)

#             session.doc_id = doc_id
#             st.session_state.pdf_loaded = True
#         st.success(f"PDF processed: {len(chunks)} chunks indexed")

#     if st.button("Reset session"):
#         st.session_state.clear()
#         st.rerun()

# # --- main chat area ---
# for role, content in st.session_state.chat_history:
#     with st.chat_message(role):
#         st.write(content)

# user_input = st.chat_input("Ask a question about your data or document...")

# if user_input:
#     st.session_state.chat_history.append(("user", user_input))
#     with st.chat_message("user"):
#         st.write(user_input)

#     with st.chat_message("assistant"):
#         with st.spinner("Thinking..."):
#             response, chart_path = session.ask(user_input, st.session_state.chat_history[:-1])
#             st.write(response)
#             if chart_path and os.path.exists(chart_path):
#                 st.image(chart_path)

#     st.session_state.chat_history.append(("assistant", response))

##---------------------------CHANGES---------------------------------------

import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

from agent.agent import AgentSession
from tools.data_tools import load_csv, clean_data
from tools.rag_tools import extract_and_chunk, embed_and_store

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "")

st.set_page_config(page_title="DataMind AI", page_icon="◆", layout="wide")

# --- theme: fonts + component overrides ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* header */
.dm-header { display: flex; align-items: baseline; gap: 0.6rem; margin-bottom: 0.1rem; }
.dm-title { font-family: 'Sora', sans-serif; font-weight: 800; font-size: 2.1rem;
            color: #E8EEF3; letter-spacing: -0.02em; }
.dm-title .accent { color: #4FD1C5; }
.dm-subtitle { font-family: 'Inter', sans-serif; color: #8A97A5; font-size: 0.95rem;
               margin-bottom: 1.1rem; }

/* live status strip — the signature element */
.dm-status { display: flex; gap: 1.4rem; padding: 0.65rem 1rem; background: #131A21;
             border: 1px solid #232D38; border-radius: 8px; margin-bottom: 1.6rem;
             font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #8A97A5; }
.dm-status .item { display: flex; align-items: center; gap: 0.45rem; }
.dm-dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
.dm-dot.on { background: #4ADE80; box-shadow: 0 0 6px #4ADE80; }
.dm-dot.off { background: #3A4552; }
.dm-status .label { color: #E8EEF3; }

/* sidebar */
section[data-testid="stSidebar"] { background: #0E141A; border-right: 1px solid #1E2731; }
.dm-eyebrow { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; letter-spacing: 0.12em;
              color: #4FD1C5; text-transform: uppercase; margin-bottom: 0.3rem; }

/* chat bubbles */
div[data-testid="stChatMessage"] { background: #131A21; border: 1px solid #1E2731;
    border-radius: 10px; padding: 0.4rem 0.2rem; }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="dm-header"><span style="font-size:1.8rem;">◆</span>'
    '<span class="dm-title">DataMind <span class="accent">AI</span></span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="dm-subtitle">Conversational data analyst — ask questions '
    'about your CSV or PDF in plain English.</div>',
    unsafe_allow_html=True,
)

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

# --- live status strip (signature element) ---
csv_dot = "on" if st.session_state.csv_loaded else "off"
pdf_dot = "on" if st.session_state.pdf_loaded else "off"
st.markdown(f"""
<div class="dm-status">
  <div class="item"><span class="dm-dot {csv_dot}"></span>CSV&nbsp;<span class="label">{"loaded" if st.session_state.csv_loaded else "not loaded"}</span></div>
  <div class="item"><span class="dm-dot {pdf_dot}"></span>PDF&nbsp;<span class="label">{"indexed" if st.session_state.pdf_loaded else "not loaded"}</span></div>
  <div class="item"><span class="dm-dot on"></span>MODEL&nbsp;<span class="label">gemini-flash-latest</span></div>
</div>
""", unsafe_allow_html=True)

# --- sidebar: uploads ---
with st.sidebar:
    st.markdown('<div class="dm-eyebrow">Data sources</div>', unsafe_allow_html=True)

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
            temp_path = os.path.join(tempfile.gettempdir(), pdf_file.name)
            with open(temp_path, "wb") as f:
                f.write(pdf_file.getbuffer())

            doc_id = pdf_file.name.replace(" ", "_").replace(".pdf", "")
            chunks = extract_and_chunk(temp_path)
            embed_and_store(chunks, doc_id, API_KEY)

            session.doc_id = doc_id
            st.session_state.pdf_loaded = True
        st.success(f"PDF processed: {len(chunks)} chunks indexed")

    st.markdown("<hr style='border-color:#1E2731; margin: 1.2rem 0;'>", unsafe_allow_html=True)
    if st.button("↺ Reset session", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- main chat area ---
st.markdown('<div class="dm-eyebrow" style="margin-top:0.4rem;">Chat</div>', unsafe_allow_html=True)
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