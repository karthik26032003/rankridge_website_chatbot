import json

from backend.helpers.config import settings
from backend.helpers.database import SessionLocal
from backend.helpers.services.openai_service import client
from backend.models.lead_model import Lead

EXTRACTION_PROMPT = """
You extract the user's email address from a chat conversation for an IIT-JEE coaching institute chatbot.

Read the conversation and return ONLY a JSON object with this key:
email

Rules:
- Use only an email address the user actually typed, never guess or invent one.
- If no email was mentioned, set email to null.
- Return valid JSON only, no extra text.

Conversation:
{transcript}
""".strip()


def _build_transcript(messages) -> str:
    lines = [
        f"{message.role}: {message.content}"
        for message in messages
        if message.role in ("user", "assistant")
    ]
    return "\n".join(lines)


def extract_and_save_lead(chat_id: str, messages) -> None:
    transcript = _build_transcript(messages)

    if not transcript:
        return

    try:
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": "You output only valid JSON, nothing else."},
                {"role": "user", "content": EXTRACTION_PROMPT.format(transcript=transcript)},
            ],
            temperature=0,
            stream=False,
        )

        extracted = json.loads(response.choices[0].message.content.strip())
    except Exception:
        return

    email = extracted.get("email")

    if not email:
        return

    db = SessionLocal()

    try:
        lead = db.query(Lead).filter(Lead.chat_id == chat_id).first()

        if not lead:
            lead = Lead(chat_id=chat_id)
            db.add(lead)

        lead.email = email
        db.commit()
    finally:
        db.close()


def get_all_leads() -> list[dict]:
    db = SessionLocal()

    try:
        leads = db.query(Lead).order_by(Lead.updated_at.desc()).all()

        return [
            {
                "chat_id": lead.chat_id,
                "email": lead.email,
                "updated_at": lead.updated_at.isoformat() if lead.updated_at else None,
            }
            for lead in leads
        ]
    finally:
        db.close()
