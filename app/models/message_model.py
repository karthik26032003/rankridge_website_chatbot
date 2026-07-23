from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.database import Base


class MessageDB(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, ForeignKey("chats.chat_id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)