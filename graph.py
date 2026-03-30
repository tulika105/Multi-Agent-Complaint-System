from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from state import AgentState

from agents.supervisor import supervisor_node
from agents.complaint_agent import complaint_node
from agents.info_agent import info_node
from agents.human_node import human_node
from agents.notify_customer_node import notify_customer_node

from tools.email_tool import email_tool


builder =  StateGraph(AgentState)

builder.add_node("supervisor", supervisor_node)
builder.add_node("complaint", complaint_node)
builder.add_node("info", info_node)
builder.add_node("human", human_node)
builder.add_node("notify_customer", notify_customer_node)
builder.add_node("email", email_tool)

builder.set_entry_point("supervisor")


def route_intent(state):
    return state["intent"]




def route_approval(state):
    return state["approval"]


builder.add_conditional_edges(
    "supervisor",
    route_intent,
    {
        "complaint": "complaint",
        "general": "info"
    }
)

builder.add_edge("info", END)

def route_urgency(state):
    urgency = state.get("urgency")
    if urgency in ["LOW", "MEDIUM", "HIGH"]:
        return urgency
    return "incomplete"


builder.add_conditional_edges(
    "complaint",
    route_urgency,
    {
        "LOW": "email",
        "MEDIUM": "email",
        "HIGH": "human",
        "incomplete": END
    }
)

builder.add_conditional_edges(
    "human",
    route_approval,
    {
        "yes": "email",
        "no": "notify_customer"
    }
)

builder.add_edge("notify_customer", END)
builder.add_edge("email", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_after=["supervisor"], interrupt_before=["human"])