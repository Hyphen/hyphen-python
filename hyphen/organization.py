from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel

if TYPE_CHECKING:
    from hyphen.client import HTTPRequestClient


class Organization(BaseModel):
    id: Optional[str]
    name: str

class OrganizationFactory:

    def __init__(self, client:"HTTPRequestClient"):
        self.client = client

    def create(self, name:str) -> "Organization":
        """Create a new organization"""
        return self.client.post("api/organizations", Organization, name=name)
