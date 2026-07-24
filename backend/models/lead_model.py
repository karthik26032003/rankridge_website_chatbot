from sqlalchemy import Column, String, DateTime, ForeignKey, func
from backend.helpers.database import Base


class Lead(Base):
    __tablename__ = "leads"

    chat_id = Column(String, ForeignKey("chats.chat_id"), primary_key=True)
    email = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
