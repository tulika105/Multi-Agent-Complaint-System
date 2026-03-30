from services.llm_service import call_llama
from services.email_service import send_email


def email_tool(state):
    # 🔹 Extract required data
    issue = state.get("issue")
    urgency = state.get("urgency")
    complaint_id = state.get("complaint_id")
    to_email = state.get("user_email")
    order_id = state.get("order_id")

    # 🔒 Safety check: email must exist
    if not to_email:
        return {
            "response": "No email provided. Cannot send notification.",
            "flow": [{
                "agent": "Notification Service",
                "log": f"Could not send email for complaint {complaint_id} (email missing)."
            }]
        }

    # 🔒 Safety check: all complaint details must be present before sending
    missing = []
    if not order_id or str(order_id).upper() == "NONE":
        missing.append("Order ID")

    if missing:
        return {
            "response": f"⚠️ Email not sent. Missing required complaint details: {', '.join(missing)}. Please re-submit with Order ID.",
            "flow": [{
                "agent": "Notification Service",
                "log": f"Email blocked for complaint {complaint_id} due to missing {', '.join(missing)}."
            }]
        }

    # 🔹 Tone by severity
    urgency_tone = {
        "LOW": "polite acknowledgment",
        "MEDIUM": "reassuring and informative",
        "HIGH": "urgent and priority escalation"
    }.get(urgency, "professional")

    # 🔹 Prompt for email generation
    prompt = f"""
    You are NEO, a customer support assistant.

    Write a professional email regarding a customer complaint. Use the details below:

    - Complaint ID: {complaint_id}
    - Order ID: {order_id}
    - Issue: {issue}
    - Tone: {urgency_tone}

    Address the customer as 'Dear customer'. Keep the email concise and professional.
    Use clear paragraph spacing for better readability (a newline after the salutation and between main points).

    Output in the following format:
    Subject: [Urgent/Update]: Complaint ID {complaint_id} - [Short Description of Issue]
    ---
    [Email Body]

    End the email body with:
    Best regards,
    NEO
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
        subject_line = f"Re: Complaint ID {complaint_id} - Update on Your Order"
        email_content = raw_response

    # 🔹 Send email
    send_email(
        to_email=to_email,
        subject=subject_line,
        body=email_content
    )

    # ✅ Standardize return data
    return {
        "response": f"Your complaint has been processed. Please check your email ({to_email}) for the formal response.",
        "flow": [{
            "agent": "Notification Service",
            "log": f"Sent formal response email to {to_email} for complaint {complaint_id} (Urgency: {urgency})."
        }]
    }