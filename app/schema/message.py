from pydantic import BaseModel


class Message(BaseModel):
    id: int | None = None
    role: str
    content: str