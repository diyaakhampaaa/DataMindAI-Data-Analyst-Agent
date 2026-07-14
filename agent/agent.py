"""
P2 owns this file — LLM / Agent Engineer.

Wraps P1's data tools and P3's RAG tool as LangChain @tool functions,
then builds a LangGraph ReAct agent that picks the right tool per
question. State (chat history) is passed in and returned each call —
P4's Streamlit app owns persisting it between turns.
"""
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from tools import data_tools
from tools import rag_tools
from agent.prompts import SYSTEM_PROMPT


class AgentSession:
    """
    Holds the current DataFrame + doc_id + API key for one user session,
    and exposes the tools the agent can call bound to that state.
    P4 creates one of these per Streamlit session.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.df = None          # set after CSV upload
        self.doc_id = None      # set after PDF upload
        self.last_chart_path = None

        self.llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", api_key=api_key)
        self.tools = self._build_tools()
        self.graph = create_react_agent(self.llm, self.tools, prompt=SYSTEM_PROMPT)

    def _build_tools(self):
        session = self  # closures below capture session state, not globals

        @tool
        def stats_tool(column: str) -> dict:
            """Get mean, median, min, max, std, count for a numeric column in the uploaded CSV."""
            if session.df is None:
                return {"error": "No CSV uploaded yet."}
            return data_tools.get_stats(session.df, column)

        @tool
        def filter_tool(column: str, condition: str, value: str) -> str:
            """Filter CSV rows. condition is one of ==, !=, >, <, >=, <=."""
            if session.df is None:
                return "No CSV uploaded yet."
            result = data_tools.filter_data(session.df, column, condition, value)
            return result.to_string(index=False)

        @tool
        def group_by_tool(group_col: str, agg_col: str, agg_func: str = "mean") -> str:
            """Group CSV rows by group_col and aggregate agg_col with agg_func (mean/sum/count/min/max)."""
            if session.df is None:
                return "No CSV uploaded yet."
            result = data_tools.group_by(session.df, group_col, agg_col, agg_func)
            return result.to_string(index=False)

        @tool
        def top_n_tool(column: str, n: int = 5, ascending: bool = False) -> str:
            """Get top or bottom N rows of the CSV sorted by column."""
            if session.df is None:
                return "No CSV uploaded yet."
            result = data_tools.top_n(session.df, column, n, ascending)
            return result.to_string(index=False)

        @tool
        def correlate_tool(col1: str, col2: str) -> dict:
            """Compute Pearson correlation between two numeric CSV columns."""
            if session.df is None:
                return {"error": "No CSV uploaded yet."}
            return data_tools.correlate(session.df, col1, col2)

        @tool
        def chart_tool(chart_type: str, x: str, y: str = None) -> str:
            """
            Generate a chart from the uploaded CSV. chart_type is one of
            bar/line/scatter/pie. Use whenever the user asks to see/plot/visualize data.
            """
            if session.df is None:
                return "No CSV uploaded yet."
            result = data_tools.make_chart(session.df, chart_type, x, y, save_path="current_chart.png")
            if "chart_path" in result:
                session.last_chart_path = result["chart_path"]
                return "Chart generated successfully."
            return str(result)

        @tool
        def document_qa_tool(question: str) -> str:
            """
            Answer a question using the uploaded PDF document via RAG retrieval.
            Use this for any question about document/paper/report content,
            NOT for questions about the CSV dataset.
            """
            if session.doc_id is None:
                return "No PDF uploaded yet."
            return rag_tools.rag_query(question, session.doc_id, session.api_key)

        return [stats_tool, filter_tool, group_by_tool, top_n_tool,
                correlate_tool, chart_tool, document_qa_tool]

    def ask(self, user_message: str, chat_history: list) -> tuple[str, str | None]:
        """
        Runs one turn of the agent. chat_history is a list of
        (role, content) tuples from previous turns. Returns
        (response_text, chart_path_or_none).
        """
        self.last_chart_path = None

        messages = []
        for role, content in chat_history:
            if role == "user":
                messages.append(HumanMessage(content=content))
            else:
                messages.append(AIMessage(content=content))
        messages.append(HumanMessage(content=user_message))

        result = self.graph.invoke({"messages": messages})
        response_text = result["messages"][-1].content

        return response_text, self.last_chart_path
