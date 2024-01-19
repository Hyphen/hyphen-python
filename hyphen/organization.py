from typing import TYPE_CHECKING, Optional, List, Union
from pydantic import BaseModel

if TYPE_CHECKING:
    from hyphen.client import HTTPRequestClient, AsyncHTTPRequestClient


class Organization(BaseModel):
    id: Optional[str]
    name: str

class OrganizationFactory:

    def __init__(self, client:Union["HTTPRequestClient","AsyncHTTPRequestClient"]):
        self.client = client

    def create(self, name:str) -> "Organization":
        """Create a new organization"""
        return self.client.post("api/organizations", Organization, name=name)

    def read(self, id:str) -> "Organization":
        """Read an organization"""
        return self.client.get(f"api/organizations/{id}", Organization)

    def list(self) -> "Organization":
        """List all organizations"""

        class OrganizationList(BaseModel):
            data: List[Organization]

            def __iter__(self):
                return iter(self.data)

            def __getitem__(self, item):
                return self.data[item]

        return self.client.get("api/organizations", OrganizationList)

class AsyncOrganizationFactory(OrganizationFactory):

    async def create(self, name:str) -> "Organization":
        """Create a new organization"""
        return await self.client.post("api/organizations", Organization, name=name)

    async def read(self, id:str) -> "Organization":
        """Read an organization"""
        return await self.client.get(f"api/organizations/{id}", Organization)

    async def list(self) -> "Organization":
        """List all organizations"""

        class OrganizationList(BaseModel):
            data: List[Organization]

            def __iter__(self):
                return iter(self.data)

            def __getitem__(self, item):
                return self.data[item]

        return await self.client.get("api/organizations", OrganizationList)