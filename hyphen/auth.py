from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, model_validator, Field


class Bearer(str, Enum):
    Bearer = "Bearer"


class Auth(BaseModel):
    expires_in: int = Field(..., alias="access_token_expires_in")
    expires_at: datetime = Field(..., alias="access_token_expires_at")
    token_type: Bearer
    access_token: str
    id_token: Optional[str] = None

    @model_validator(mode="before")
    def set_expires(cls, v):
        """exp are mongodb native times"""
        v["access_token_expires_in"] = v["access_token_expires_in"] / 1000
        v["access_token_expires_at"] = datetime.fromtimestamp(
            (v["access_token_expires_at"] / 1000)
        )
        return v
