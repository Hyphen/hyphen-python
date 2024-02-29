from typing import Literal, Optional, Any, List
from pydantic import BaseModel, model_validator, model_serializer


class Role(BaseModel):
    name: str
    context: Optional[Literal["organization", "team"]] = None
    context_id: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def string_role(cls, value: Any) -> Any:
        if isinstance(value, str):
            return {"name": value}
        return value

    @model_serializer
    def serialize(self) -> dict:
        return self.name

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, str):
            return self.name == __value
        return super().__eq__(__value)


class LocalizedRole(BaseModel):
    roles: List[str]
