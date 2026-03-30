import operator
from typing import Annotated, TypedDict, Optional, List, Dict

def flow_reducer(a: List[Dict], b: List[Dict]) -> List[Dict]:
    """
    Standard reducer adds lists. 
    However, if 'b' is empty, it acts as a RESET signal 
    (used to start a fresh trace for a new turn in a persistent session).
    """
    if b == []:
        return []
    return a + b

class AgentState(TypedDict):
    # 🔹 Session-level fields
    session_id: int
    initial_query: str
    phase: str  # "idle", "processing", "completed"
    next_node: Optional[str]

    # 🔹 Input
    user_query: str
    user_email: Optional[str]

    # 🔹 Supervisor output
    intent: Optional[str]  # "complaint" or "general"

    # 🔹 Complaint details
    issue: Optional[str]
    order_id: Optional[str]
    urgency: Optional[str]  # LOW / MEDIUM / HIGH
    complaint_id: Optional[str]

    # 🔹 Human-in-the-loop
    approval: Optional[str]  # "yes" or "no"

    # 🔹 Final response
    response: Optional[str]

    # 🔹 Execution trace 
    flow: Annotated[List[Dict], flow_reducer]