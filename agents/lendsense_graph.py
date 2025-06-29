
import os, uuid, datetime
from typing import Annotated, List


from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_tavily import TavilySearch
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
# from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3


from tools.loan_calc import run_loan_calc
from tools.eligibility import check_eligibility
from tools.doc_parser import parse_pan, parse_aadhaar
from memory.mcp_memory import MCPMemory

LLM = init_chat_model("google_genai:gemini-2.0-flash", temperature=0.1)

@tool(description="Compute EMI & total payment for a loan principal (INR).")
def LoanCalculator(amount: float) -> dict:
    return run_loan_calc(principal=amount)

@tool(description="Check FOIR (≤40 %) and LTV (≤80 %) eligibility.")
def EligibilityChecker(net_salary: float, emi: float, ltv: float) -> dict:
    return check_eligibility(net_salary, emi, ltv)

@tool(description="Extract PAN & Aadhaar numbers from raw text.")
def DocumentParser(text: str) -> dict:
    d = {}
    d.update(parse_pan(text))
    d.update(parse_aadhaar(text))
    return d

search_tool = TavilySearch(
    max_results=2,
    description="Search the web when domain tools are insufficient."
)

TOOLS = [LoanCalculator, EligibilityChecker, DocumentParser, search_tool]

llm_with_tools = LLM.bind_tools(TOOLS)

from typing_extensions import TypedDict
class State(TypedDict):
    messages: Annotated[List, add_messages]   

builder = StateGraph(State)

def chatbot(state: State):
    """LLM node that may emit tool_calls."""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools=TOOLS))


builder.add_conditional_edges("chatbot", tools_condition)
builder.add_edge("tools", "chatbot")
builder.add_edge(START, "chatbot")


# checkpointer = MemorySaver()
# checkpointer = SqliteSaver("checkpoints.db")# change to SqliteSaver("chat.db") in prod
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(conn) 
graph = builder.compile(checkpointer=checkpointer)

mcp = MCPMemory()

def run_lendsense(user_text: str, thread_id: str = "default") -> str:
    """
    Process one user turn and persist chat state.
    `thread_id` keeps memory separate for parallel conversations.
    """
    user_msg = HumanMessage(content=user_text)
    
    config = {"configurable": {"thread_id": thread_id}}
    final_state = None
    for state in graph.stream({"messages": [user_msg]}, config, stream_mode="values"):
        final_state = state
        # adds each state to final_state object

    if final_state is None or not final_state.get("messages"):
        raise RuntimeError("Agent produced no output.")

    messages = final_state["messages"]
    assistant_msg = messages[-1]
    reply = getattr(assistant_msg, "content", "")
    
    def _serialize(msg):
        base = {
            "type": msg.__class__.__name__,
            "content": getattr(msg, "content", "")
        }
        if isinstance(msg, ToolMessage):
            base["tool_name"] = msg.name
        return base

    serialised_msgs = [_serialize(m) for m in messages]
    tool_calls = [_serialize(m) for m in messages if isinstance(m, ToolMessage)]
    
    mcp.append({
        "id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "thread_id": thread_id,
        "messages": serialised_msgs,
        "tool_calls": tool_calls,
        "outcome": reply,
        "self_reflection": ""
    })

    return reply


if __name__ == "__main__":
    print("👋  LendSense-Gemini ready. Type 'exit' to quit.")
    while True:
        msg = input("\nUser: ").strip()
        if msg.lower() in {"exit", "quit"}:
            break
        print("Assistant:", run_lendsense(msg, thread_id="1"))
