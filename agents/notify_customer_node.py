from services.llm_service import call_llama
from services.email_service import send_email


def notify_customer_node(state):
    """
    Sends a polite closure email to the customer when a HIGH severity
    escalation is rejected by the human agent.
    Signs off as ZARA, Customer Support Assistant.
    """
    to_email = state.get("user_email")
    complaint_id = state.get("complaint_id")
    issue = state.get("issue")
    order_id = state.get("order_id")

    # 🔒 Safety check: email must exist
    if not to_email:
        return {
            "flow": [{
                "agent": "Notification Service",
                "log": f"Could not send notification for complaint {complaint_id} (email missing)."
            }]
        }

    # 🔹 Generate polite closure email signed as ZARA
    prompt = f"""
    You are ZARA, a customer support assistant.

    A customer's complaint was reviewed but could not be escalated at this time.
    Write a short, polite, and empathetic email to inform them.

    Details:
    - Complaint ID: {complaint_id}
    - Order ID: {order_id if order_id else "N/A"}
    - Issue: {issue}

    Address the customer as 'Dear customer'. Tone: Apologetic, reassuring, and professional.
    Let them know their complaint is on record and the support team will follow up.
    Keep it concise (3-4 sentences max).

    Use clear paragraph spacing for better readability (a newline after the salutation and between main points).

    Output in the following format:
    Subject: Complaint Update: ID {complaint_id} - [Short Status Summary]
    ---
    [Email Body]

    End the email body with:
    Best regards,
    ZARA
    Customer Support Assistant
    """

    # 🔹 Generate email content
    raw_response = call_llama(prompt)

    # 🔹 Parse subject and body
    if "---" in raw_response:
        parts = raw_response.split("---", 1)
        subject_line = parts[0].replace("Subject:", "").strip()
        email_content = parts[1].strip()
    else:
        subject_line = f"Re: Complaint ID {complaint_id} - Update on Your Request"
        email_content = raw_response

    # 🔹 Send the email
    send_email(
        to_email=to_email,
        subject=subject_line,
        body=email_content
    )

    # ✅ Standardize return data
    return {
        "response": f"Escalation declined. A formal notification has been sent to {to_email}.",
        "flow": [{
            "agent": "Notification Service",
            "log": f"Notifying customer regarding complaint {complaint_id}."
        }]
    }
