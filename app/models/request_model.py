from pydantic import BaseModel


class RequestModel(BaseModel):
    user_message: str
