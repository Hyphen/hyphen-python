from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel
from hyphen.base_factory import BaseFactory


if TYPE_CHECKING:
    from hyphen.client import HTTPRequestClient, AsyncHTTPRequestClient

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

class OrganizationFactory(BaseFactory):
    url_path: str
    _object_class = Organization

    def __init__(self, client:"HTTPRequestClient"):
        super().__init__(client)
        self.url_path = "api/organizations"

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

    def expunge(self, organization: "Organization") -> None:
        """Delete an organization perminantly and forever"""
        return self.client.delete(f"{self.url_path}/api/internal/expunge/organization/{organization.id}")


class AsyncOrganizationFactory(OrganizationFactory):

    def __init__(self, client:"AsyncHTTPRequestClient"):
        super().__init__(client)

    async def list(self) -> "Organization":
        """List all organizations"""

        class OrganizationList(BaseModel):
            data: List[Organization]

            def __iter__(self):
                return iter(self.data)

            def __getitem__(self, item):
                return self.data[item]

        return await self.client.get(self.url_path, OrganizationList)

    async def expunge(self, organization: "Organization") -> None:
        """Delete an organization perminantly and forever"""
        return self.client.delete(f"{self.url_path}/api/internal/expunge/organization/{organization.id}")