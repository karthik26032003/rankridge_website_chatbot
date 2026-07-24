from backend.helpers.config import get_system_prompt
from backend.helpers.services.memory_service import (
    get_chat_messages,
    add_user_message,
    add_assistant_message,
)
from backend.helpers.services.lead_service import extract_and_save_lead
from backend.helpers.services.openai_service import stream_ai_response


def build_messages_for_chat(chat_id: str):
    db_messages = get_chat_messages(chat_id)

    if not db_messages:
        return []

    formatted = [
        {"role": message.role, "content": message.content}
        for message in db_messages
    ]

    return [{"role": "system", "content": get_system_prompt()}] + formatted


def start_chat_message(chat_id: str, user_message: str) -> int:
    return add_user_message(chat_id, user_message)


def stream_chat_response(chat_id: str):
    messages = build_messages_for_chat(chat_id)

    if not messages:
        return

    full_response = ""

    try:
        for chunk in stream_ai_response(messages):
            full_response += chunk
            yield chunk
    except Exception:
        yield "\n\n[Error: failed to get a response from the AI service.]"
        return

    if full_response:
        add_assistant_message(chat_id, full_response)
        extract_and_save_lead(chat_id, get_chat_messages(chat_id))
