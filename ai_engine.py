
import json
from groq import Groq

client = Groq(api_key="gsk_PsWvVo84hZWoVMCl0dsmWGdyb3FYbIgHP5ZRUKpq5Sb6ncQlf3MZ111")

def get_pc_action(user_command):
    """
    Converts user voice/text command into a JSON action.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """
You are a virtual assistant with playful tone.

- If user wants to open a website and search, ALWAYS respond in JSON like:
{
  "type": "command",
  "action": "website_search",
  "site": "youtube",
  "query": "lo-fi beats"
}

- If user wants to control apps/windows, respond in JSON like:
{
  "type": "command",
  "action": "open_app",
  "app": "chrome"
}

- For normal chat, respond in JSON like:
{
  "type": "chat",
  "response": "Hey there! 😏"
}

- NO extra text, return only JSON.
"""
            },
            {
                "role": "user",
                "content": user_command
            }
        ],
        temperature=0
    )

    reply = response.choices[0].message.content.strip()

    try:
        return json.loads(reply)
    except json.JSONDecodeError:
        return {
            "type": "chat",
            "response": "Sorry sir, I had trouble understanding that."
        }

