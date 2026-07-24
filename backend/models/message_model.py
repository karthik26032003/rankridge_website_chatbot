from sqlalchemy import Column, Integer, String, Text, ForeignKey
from backend.helpers.database import Base


class MessageDB(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    # Indexed: every read filters messages by chat_id.
    chat_id = Column(String, ForeignKey("chats.chat_id"), nullable=False, index=True)
    role = Column(String, nullable=False)
    # Text (not String) so long assistant replies aren't length-capped on
    # databases where String maps to a bounded VARCHAR.
    content = Column(Text, nullable=False)