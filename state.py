import operator
from typing import Annotated, TypedDict, Optional, List, Dict

def flow_reducer(a: List[Dict], b: List[Dict]) -> List[Dict]:
    """
    Combines the existing history (a) with the new update (b).
    
    Why use this? 
    It prevents any agent from OVERWRITING the work of the previous one.
    
    Example:
    1. WITHOUT this reducer:
       If Agent 1 writes ["A"] and Agent 2 writes ["B"], the result is only ["B"].
    2. WITH this reducer:
       If Agent 1 writes ["A"] and Agent 2 writes ["B"], the result is ["A", "B"].
       
    - If 'b' is [], it resets the state (Clears history).
    - Otherwise, it adds 'b' to the end of 'a' (Appends update).
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