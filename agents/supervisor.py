from services.llm_service import call_llama


def supervisor_node(state):
    user_query = state["user_query"]

    prompt = f"""
    Classify the user intent into ONLY one word based on the query:

    - complaint → If the user is reporting a NEW issue, a specific problem with an order, or filing formal dissatisfaction.
    - general   → If the user is greeting, saying thanks/okay, asking a general follow-up question, or checking status of something already mentioned.

    Output strictly: complaint OR general

    Query: {user_query}
    """

    result = call_llama(prompt).strip().lower()

    # 🔒 Safety fallback
    if result not in ["complaint", "general"]:
        result = "general"

    # 🔹 Return the updated state. Reset complaint fields if intent is general.
    response = {
        "intent": result,
        "flow": [{
            "agent": "Customer Service Router",
            "log": "Categorizing your inquiry..."
        }]
    }

    if result == "general":
        response.update({
            "urgency": None,
            "issue": None,
            "order_id": None,
            "complaint_id": None
        })

    return response
