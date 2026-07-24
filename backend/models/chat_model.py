from sqlalchemy import Column, String
from backend.helpers.database import Base


class Chat(Base):
    __tablename__ = "chats"

    chat_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)