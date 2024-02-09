from typing import Optional, List
from pydantic import BaseModel

class Organization(BaseModel):
    """A company or group representation within the Hyphen.ai API.

    All assets at Hyphen belong to an Organization. While it is unusual for a Member to belong to more than one Organization, it is possible;
    the [`HyphenClient`][hyphen.client.HyphenClient] will attempt to determine the correct Organization to use based on the credentials provided, but you will need to specify an
    organization id if the credentials are ambiguous.
    """
    id: Optional[str] = None
    name: str
    phone_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None

class OrganizationFactory():
    url_path: str

    def __init__(self, client):
        """Note: Organization is the only factory that does not inherit from `BaseFactory` because it is used to determine the organization associated with the credentials."""
        self.client = client
        self.url_path = "api/organizations"

    def create(self, name:str) -> "Organization":
        """Create a new organization"""
        instance = Organization(name=name)
        return self.client.post(self.url_path, Organization, instance)

    def read(self, id:str) -> "Organization":
        """Read an organization"""
        return self.client.get(f"{self.url_path}/{id}", Organization)

    def list(self) -> "Organization":
        """List all organizations available with the provided credentials.
        """

        class OrganizationList(BaseModel):
            data: List[Organization]

            def __iter__(self):
                return iter(self.data)

            def __getitem__(self, item):
                return self.data[item]

        return self.client.get(self.url_path, OrganizationList)

class AsyncOrganizationFactory(OrganizationFactory):

    async def create(self, name:str) -> "Organization":
        """Create a new organization"""
        instance = Organization(name=name)
        return self.client.post(self.url_path, Organization, instance)

    async def read(self, id:str) -> "Organization":
        """Read an organization"""
        return await self.client.get(f"{self.url_path}/{id}", Organization)

    async def list(self) -> "Organization":
        """List all organizations"""

        class OrganizationList(BaseModel):
            data: List[Organization]

            def __iter__(self):
                return iter(self.data)

            def __getitem__(self, item):
                return self.data[item]

        return await self.client.get(self.url_path, OrganizationList)