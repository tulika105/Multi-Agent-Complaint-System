# Codebase Overview: Multi-Agent Complaint System

This document provides a comprehensive overview of the Multi-Agent Complaint System. The system is built using **LangGraph** to coordinate multiple LLM agents (powered by Groq/Llama-3 and Google Gemini) which process customer inquiries, classify complaints, assess urgency, loop in human reviewers when needed, and automate email responses.

---

## 🏗️ Core Application Files

### `main.py`
The entry point of the application. It runs the main conversation loop using a visually appealing `rich` Command Line Interface (CLI). 
- Captures user input.
- Initializes and invokes the LangGraph state machine.
- Manages **Interrupts**: It halts the graph contextually to ask the user for their email (if filing a complaint) or to ask a manager to approve an escalation.
- Interacts with the `logger` utility to record session states (idle, processing, completed).

### `graph.py`
Defines the architectural backbone of the system using LangGraph (`StateGraph`).
- Registers all agents as **nodes** (e.g., `supervisor`, `complaint`, `info_agent`).
- Connects nodes with **edges** and **conditional edges** based on the state (e.g., routing to `complaint` or `info` based on intent; routing to `human_node` if severity is HIGH).
- Utilizes `MemorySaver` to checkpoint progress and allow pausing/resuming for human-in-the-loop interactions.

### `state.py`
Defines the structure of the data passing between nodes. 
- Implements `AgentState` as a `TypedDict`.
- Maintains critical variables: `session_id`, `user_query`, `intent`, `urgency`, `approval`.
- Implements a custom `flow_reducer` to accumulate logs across conversation turns to build a comprehensive history of agent actions.

---

## 🤖 Agents (`/agents/`)

Agents represent the distinct logic nodes within the LangGraph setup. 

### `supervisor.py`
The initial routing node. It sends the `user_query` to a Llama model to categorize the user's intent purely as either `complaint` or `general`. It updates the state so `graph.py` can route appropriately.

### `complaint_agent.py`
Handles queries classified as complaints. It uses a Llama model to extract the core `issue`, `order_id`, and categorizes the `urgency` (LOW, MEDIUM, HIGH). Validation logic ensures an order ID exists before proceeding, and generates a unique `complaint_id`. 

### `info_agent.py`
Handles general queries. Uses the `gemini-2.5-flash` model to act as a professional Customer Support Assistant, answering basic questions or offering polite replies when no explicit complaint is filed.

### `human_node.py`
Acts as a programmatic milestone for HIGH-urgency complaints. The actual "Wait, let me review this" pause happens in `main.py` via an interrupt, but this node records the outcome (Escalation Approved/Declined) into the execution flow.

### `notify_customer_node.py`
Triggered if the Human Reviewer rejects an escalation. It generates a polite, personalized rejection/follow-up email (signed by "ZARA") using Llama and directly triggers the `email_service` to notify the customer safely.

---

## 🛠️ Tools & Services 

### `tools/email_tool.py`
A distinct tool node in the LangGraph that structures the final automated response email when lower urgency complaints are processed, or human escalations are approved. Formats the complaint ID, issue, and urgency neatly before dispatching.

### `services/email_service.py`
A simple utility script utilizing Python's built-in `smtplib` and `MIMEText`. Connects to Gmail's SMTP server using credentials loaded from `.env` to actually send emails out over the internet.

### `services/llm_service.py`
Abstracts the interactions with external large language models.
- Provides `call_llama()` to interface with Groq's `llama-3.3-70b-versatile` API (used for precise routing and extraction).
- Provides `call_gemini()` to interface with Google's GenAI `gemini-2.5-flash` (used for conversational general responses).

---

## 📂 Utilities & Data

### `utils/logger.py`
A comprehensive script that standardizes how data is saved to disk for human readability and record keeping.
- `update_session_log()`: Keeps a cumulative, persistent trace of a user's session over multiple turns (idle -> processing -> completed). Saves to `session_logs.json`.
- `save_complaint()`: Extracts valid, processed complaints and saves them distinctly into `complaints.json`.

### `utils/id_generator.py`
A tiny utility to abstract the creation of random, alphanumeric `complaint_ids` for tracking tickets.

### `/data/` Directory
The storage directory where `session_logs.json` (running conversation histories and system traces) and `complaints.json` (successful complaint reports) are persisted by the logger.
