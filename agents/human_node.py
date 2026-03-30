def human_node(state):
    """
    This node now acts as a logging and confirmation step.
    The actual 'approval' decision is injected into the state
    by the external handler (main.py) during the graph interrupt.
    """
    approval = state.get("approval")

    # 🔹 Return the updated state. Annotated 'flow' will merge automatically.
    return {
        "flow": [{
            "agent": "Escalation Desk",
            "log": f"Manual review completed: Escalation {'Approved' if approval == 'yes' else 'Declined'}."
        }]
    }