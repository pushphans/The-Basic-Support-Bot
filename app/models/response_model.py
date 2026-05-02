from pydantic import BaseModel


class ResponseModel(BaseModel):
    ai_response: str
    intent: str
