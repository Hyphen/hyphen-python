from typing import TYPE_CHECKING, Optional, List, Union, Any
from pydantic import BaseModel

if TYPE_CHECKING:
    from hyphen.client import HTTPRequestClient, AsyncHTTPRequestClient


class Member(BaseModel):
    id: Optional[str]
    name: str

class MemberFactory:

    def __init__(self, client:Union["HTTPRequestClient","AsyncHTTPRequestClient"]):
        self.client = client

        # not implemented stubber, just until endpoints are implemented
        class NotImplementedStub:
            def __getattr__(self, name:"Any"):
                raise NotImplementedError("Members is not implemented in hyphen.ai yet")
        self.client = NotImplementedStub

    def create(self, name:str) -> "Member":
        """Create a new member, within the context of the current organization"""
        return self.client.post("api/members", Member, name=name)

    def read(self, id:str) -> "Member":
        """Read a member"""
        return self.client.get(f"api/members/{id}", Member)

    def list(self) -> "Member":
        """List all members"""

        class MemberList(BaseModel):
            data: List[Member]

            def __iter__(self):
                return iter(self.data)

            def __getitem__(self, item):
                return self.data[item]

        return self.client.get("api/members", MemberList)

class AsyncMemberFactory(MemberFactory):

    async def create(self, name:str) -> "Member":
        """Create a new member"""
        return await self.client.post("api/members", Member, name=name)

    async def read(self, id:str) -> "Member":
        """Read an member"""
        return await self.client.get(f"api/members/{id}", Member)

    async def list(self) -> "Member":
        """List all members"""

        class MemberList(BaseModel):
            data: List[Member]

            def __iter__(self):
                return iter(self.data)

            def __getitem__(self, item):
                return self.data[item]

        return await self.client.get("api/members", MemberList)