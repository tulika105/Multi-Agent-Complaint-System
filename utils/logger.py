import json
import os
from datetime import datetime

LOG_FILE = "data/session_logs.json"
COMPLAINT_FILE = "data/complaints.json"


def get_last_session_id():
    """
    Scans the log file to find the highest session ID used so far.
    """
    if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        return 0
    
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
            if not data:
                return 0
            return max(s.get("session_id", 0) for s in data)
    except (json.JSONDecodeError, ValueError):
        return 0


def update_session_log(state, phase):
    """
    Updates the session_logs.json with a cohesive, cumulative trace.
    Handles merge logic based on session_id to maintain one object per session.
    
    Phases:
    - 'idle': System is waiting for new input (Pre-turn).
    - 'processing': System is working on the input (Mid-turn).
    - 'completed': System has finished and provided a response (Post-turn).
    """
    session_id = state.get("session_id")
    if not session_id:
        return

    # 🔹 1. Prepare new decision log entries for this update
    new_entries = []
    
    if phase == "idle":
        # System is waiting for input
        pass
    
    elif phase == "processing":
        # Just received user input
        new_entries.append(f"[user_input] User said: '{state.get('user_query')}'")
        new_entries.append(f"[phase_transition] idle -> processing")
        
    elif phase == "completed":
        # Finished processing, has a response
        intent = state.get("intent")
        if intent:
            new_entries.append(f"[intent_classification] Intent detected: {intent}")
            new_entries.append(f"[routing_decision] Route to: {intent}")

        # Add existing flow entries
        for entry in state.get("flow", []):
            agent = entry.get("agent")
            log = entry.get("log")
            if agent and log:
                new_entries.append(f"[{agent.lower().replace(' ', '_')}] {log}")

        new_entries.append(f"[phase_transition] processing -> completed")
        new_entries.append(f"[bot_response] {state.get('response')}")

    # 🔹 2. Load and Merge
    data = []
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
        try:
            with open(LOG_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []

    # Find existing session
    existing = next((s for s in data if s.get("session_id") == session_id), None)

    if existing:
        # Update timestamp and state fields (ONLY if they are provided in this update)
        existing["timestamp"] = datetime.now().isoformat()
        existing["state"]["phase"] = phase
        
        # Ensure initial_message is eventually set
        if not existing["state"].get("initial_message"):
            existing["state"]["initial_message"] = state.get("initial_query") or state.get("user_query")

        if phase == "idle":
            existing["state"]["current_message"] = None
        elif state.get("user_query"):
            existing["state"]["current_message"] = state.get("user_query")
            
        # Update fields for this interaction
        if phase in ["processing", "completed"]:
            existing["state"]["urgency"] = state.get("urgency")
            existing["state"]["intent"] = state.get("intent")

        if state.get("response"):
            existing["state"]["bot_response"] = state.get("response")
            
        existing["state"]["next_node"] = state.get("next_node") or state.get("intent") or "completed"
        
        # Append new entries to decision_log
        existing["decision_log"].extend(new_entries)
    else:
        # Create fresh session object
        initial = state.get("initial_query") or state.get("user_query")
        new_session = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "state": {
                "current_message": state.get("user_query"),
                "initial_message": initial,
                "phase": phase,
                "intent": state.get("intent"),
                "urgency": state.get("urgency"),
                "bot_response": state.get("response"),
                "next_node": state.get("next_node") or state.get("intent") or "completed"
            },
            "decision_log": new_entries
        }
        data.append(new_session)

    # 🔹 3. Write back
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=4)


def save_complaint(state):
    # Only save if it's a complaint AND has a complaint_id (processed successfully)
    if state.get("intent") != "complaint" or not state.get("complaint_id"):
        return

    data = {
        "timestamp": datetime.now().isoformat(),
        "complaint_id": state.get("complaint_id"),
        "issue": state.get("issue"),
        "order_id": state.get("order_id"),
        "urgency": state.get("urgency"),
        "user_email": state.get("user_email")
    }

    _append_json(COMPLAINT_FILE, data)


def _get_action_desc(entry):
    agent = str(entry.get("agent", "")).lower()
    tool = str(entry.get("tool", "")).lower()
    
    if "supervisor" in agent:
        return f"Analyzing request to determine next steps"
    if "complaint" in agent:
        return "Reviewing complaint details"
    if "support assistant" in agent:
        return "Preparing response"
    if "human" in agent:
        return "Human review"
    
    return "Handling request"


def _append_json(file_path, new_data):
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    data = []
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []

    data.append(new_data)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)