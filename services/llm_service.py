import os
from dotenv import load_dotenv
from groq import Groq
from google import genai

load_dotenv()

# 🔹 API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 🔹 Clients
groq_client = Groq(api_key=GROQ_API_KEY)

gemini_client = genai.Client(api_key=GEMINI_API_KEY)


# ==============================
# 🔹 Llama (Groq) - Core Logic
# ==============================
def call_llama(prompt: str) -> str:
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"ERROR: {str(e)}"


# ==============================
# 🔹 Gemini - Info Agent
# ==============================
def call_gemini(prompt: str) -> str:
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()

    except Exception as e:
        return f"ERROR: {str(e)}"