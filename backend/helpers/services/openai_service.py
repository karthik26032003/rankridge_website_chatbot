from openai import OpenAI
from backend.helpers.config import settings

# Single shared OpenAI client for the whole app. Other modules import this
# instance instead of constructing their own.
client = OpenAI(api_key=settings.OPENAI_API_KEY)


def stream_ai_response(messages):
    stream = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=messages,
        temperature=settings.TEMPERATURE,
        max_tokens=settings.MAX_TOKENS,
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield delta.content


def generate_chat_title_from_message(message: str) -> str:
    """
    Generate a short chat title from the user's first message.
    Fallback: first 40 chars if generation fails.
    """
    prompt = f"""
Generate a very short chat title for this user message.

Rules:
- Maximum 6 words
- No quotes
- No punctuation at the end
- Make it concise and natural like a ChatGPT conversation title

User message:
{message}
""".strip()

    try:
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You create short and useful conversation titles."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            stream=False,
        )

        title = response.choices[0].message.content.strip()

        if not title:
            return message[:40].strip() or "New Chat"

        return title[:80]
    except Exception:
        return message[:40].strip() or "New Chat"