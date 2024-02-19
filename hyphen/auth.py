from datetime import datetime
from enum import Enum
from pydantic import BaseModel, model_validator


class Bearer(str, Enum):
    Bearer = "Bearer"

class Auth(BaseModel):
    expires_in: int
    expires_at: datetime
    token_type: Bearer
    access_token: str
    id_token: str

    @model_validator(mode="before")
    def set_expires(cls, v):
        """exp are mongodb native times"""
        v["expires_in"] = v["expires_in"] / 1000
        v["expires_at"] = datetime.fromtimestamp(v["expires_in"])
        return v