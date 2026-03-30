import json
from services.llm_service import call_llama
from utils.id_generator import generate_complaint_id


def complaint_node(state):
    user_query = state["user_query"]

    prompt = f"""
    You are a detail-oriented complaint processing agent.
    Extract the following from the user query:

    1. Issue: A concise summary of the problem reported by the user.
    2. Order ID: Any alphanumeric reference code (e.g., ORD-123, #456, 78910). If not clearly an order ID, output NONE.
    3. Severity:
       - HIGH → Reports of damage, missing items, or safety concerns.
       - MEDIUM → Wrong items, significant delays, or poor quality.
       - LOW → Minor grievances, general dissatisfaction, or slight delays.

    Output in this exact JSON format:

    {{
      "issue": "...",
      "order_id": "...",
      "urgency": "LOW/MEDIUM/HIGH"
    }}

    Query: {user_query}
    """

    result = call_llama(prompt)

    # 🔒 Basic parsing (safe fallback)
    issue = None
    order_id = None
    urgency = "MEDIUM"  # default fallback

    try:
        parsed = json.loads(result)
        issue = parsed.get("issue")
        order_id = parsed.get("order_id")
        urg = parsed.get("urgency", "").upper()
        if urg in ["LOW", "MEDIUM", "HIGH"]:
            urgency = urg
    except Exception:
        issue = "unknown issue"
        order_id = None
        urgency = "MEDIUM"

    # 🔒 Guard: block email if order_id or key details are missing
    missing = []
    if not order_id or order_id.upper() == "NONE":
        missing.append("Order ID")

    if missing:
        return {
            "urgency": None,
            "response": f"⚠️ Cannot process complaint. The following details are missing: {', '.join(missing)}. Please re-submit your complaint with all required information.",
            "flow": [{
                "agent": "Complaint Agent",
                "log": f"Incomplete information: {', '.join(missing)} was missing."
            }]
        }

    # 🔹 Generate complaint ID
    complaint_id = generate_complaint_id()

    # 🔹 Clean return data
    return {
        "issue": issue,
        "order_id": order_id,
        "urgency": urgency,
        "complaint_id": complaint_id,
        "flow": [{
            "agent": "Complaint Agent",
            "log": f"Analyzing your complaint regarding order {order_id} (Urgency: {urgency})."
        }]
    }