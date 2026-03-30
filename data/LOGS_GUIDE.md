# 🤖 Understanding Multi-Agent Session Logs

This guide explains how to read and interpret the interactions stored in `data/session_logs.json` and `data/complaints.json`.

---

## 📂 1. Session Logs (`session_logs.json`)
This file tracks every interaction within a conversation. Each session is identified by a unique `session_id`.

### 📍 The `state` Block
The `state` object provides a snapshot of the **most recent turn** in the session:
- **`phase`**: The current status of the engine:
    - `idle`: Waiting for user input.
    - `processing`: An agent is currently analyzing the query.
    - `completed`: The turn is finished and a response was delivered.
- **`initial_message`**: The very first query that started the entire session.
- **`current_message`**: The last message sent by the user in this session.
- **`intent`**: The detected category of the latest query (`complaint` or `general`).
- **`urgency`**: The severity level (`HIGH`, `MEDIUM`, `LOW`, or `null`).
- **`bot_response`**: The final answer provided by the AI in the last turn.
- **`next_node`**: The planned destination for the next step (e.g., `human`, `email`, or `completed`).

### 🪵 The `decision_log`
A cumulative, chronological trace of every single step taken during the session. It uses clear prefixes:
- `[user_input]`: Records exactly what the user said.
- `[phase_transition]`: Tracks the internal state changes (e.g., `idle -> processing`).
- `[intent_classification]`: Shows how the supervisor categorized the request.
- `[routing_decision]`: Where the supervisor decided to send the request.
- `[agent_name]`: Logs specific actions taken by agents (e.g., `[complaint_agent]`, `[notification_service]`).
- `[bot_response]`: Records the final output shown to the user.

---

## 📂 2. Complaints Log (`complaints.json`)
This file acts as a **clean database** of all successfully processed complaints.

### 📝 Entry Structure
- **`complaint_id`**: The unique identifier (e.g., `CMP-XXXXXX`).
- **`timestamp`**: Precisely when the complaint was recorded.
- **`issue`**: A concise summary of the problem.
- **`order_id`**: The reference number (e.g., `5666`).
- **`urgency`**: The severity of the issue.
- **`user_email`**: The customer's contact information.

---

## 🔄 Lifecycle Example
1. **User**: "My LG Fridge model A35 has broken glass."
2. **System**:
    - **Intent**: `complaint` | **Urgency**: `HIGH`
    - **Decision**: `[complaint_agent]` extracts "Broken glass" and "A35".
    - **Escalation**: `[escalation_desk]` approves the request.
    - **Notification**: `[notification_service]` sends a formal email.
    - **Record**: A new entry appears in `complaints.json`.
3. **User**: "thanks"
    - **Intent**: `general` | **Urgency**: `null`
    - **Decision**: `[support_assistant_(axon)]` provides a polite closing.
