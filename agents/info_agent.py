from services.llm_service import call_gemini


def info_node(state):
    user_query = state["user_query"]

    prompt = f"""
    You are a highly professional and empathetic Customer Support Assistant.
    Your goal is to provide clear, helpful, and concise information to the user.

    Instructions:
    - Answer the question accurately.
    - Use bullet points for steps or lists to make them easy to read.
    - Use bold text for key terms or Order IDs.
    - End with a polite closing like "Is there anything else I can assist you with?".
    - If the user is just saying 'thanks' or 'hello', respond politely and professionally.
    
    Current User Query: {user_query}
    """

    result = call_gemini(prompt)

    # 🔹 Return the updated state
    return {
        "response": result,
        "flow": [{
            "agent": "Information Agent",
            "log": "Providing professional assistance based on the general inquiry."
        }]
    }