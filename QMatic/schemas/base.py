from pydantic import BaseModel


class RevertedMessage(BaseModel):
    msg: str | None
