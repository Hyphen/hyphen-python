from typing import Optional
from pydantic import Field, computed_field
from hyphen.base_object import RESTModel

class Slack(RESTModel):
    id: str = Field(alias="identifier")
    team_id: str
    additional_prop_1: Optional[dict] = None

    @computed_field(repr=False)
    def type(self) -> str:
        return self.__class__.__name__.lower()