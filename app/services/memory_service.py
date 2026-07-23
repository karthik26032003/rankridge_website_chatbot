from app.db.database import SessionLocal
from app.models.chat_model import Chat
from app.models.message_model import MessageDB
from app.schema.message import Message
from app.services.openAI_services import generate_chat_title_from_message


def generate_chat_title(message: str) -> str:
    return generate_chat_title_from_message(message)


def get_chat_messages(chat_id: str) -> list[Message]:
    db = SessionLocal()

    try:
        messages = (
            db.query(MessageDB)
            .filter(MessageDB.chat_id == chat_id)
            .order_by(MessageDB.id.asc())
            .all()
        )

        return [
            Message(id=message.id, role=message.role, content=message.content)
            for message in messages
        ]
    finally:
        db.close()


def add_user_message(chat_id: str, message: str) -> int:
    db = SessionLocal()

    try:
        chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()

        if not chat:
            chat = Chat(
                chat_id=chat_id,
                title=generate_chat_title(message)
            )
            db.add(chat)
            db.commit()

        db_message = MessageDB(
            chat_id=chat_id,
            role="user",
            content=message
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)

        return db_message.id
    finally:
        db.close()


def add_assistant_message(chat_id: str, message: str) -> None:
    db = SessionLocal()

    try:
        chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()

        if not chat:
            chat = Chat(
                chat_id=chat_id,
                title="New Chat"
            )
            db.add(chat)
            db.commit()

        db_message = MessageDB(
            chat_id=chat_id,
            role="assistant",
            content=message
        )
        db.add(db_message)
        db.commit()
    finally:
        db.close()