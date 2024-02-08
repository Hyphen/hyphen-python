from pydantic import BaseModel, ConfigDict
from humps.camel import case

class RESTModel(BaseModel):
    """A rest-api friendly base class"""
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=case,
        arbitrary_types_allowed=True,
    )