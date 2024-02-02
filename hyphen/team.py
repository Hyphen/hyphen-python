from typing import TYPE_CHECKING, Optional, List, Union, Any
from pydantic import BaseModel

if TYPE_CHECKING:
    from hyphen.client import HTTPRequestClient, AsyncHTTPRequestClient


class Team(BaseModel):
    id: Optional[str]
    name: str

class TeamFactory:

    def __init__(self, client:Union["HTTPRequestClient","AsyncHTTPRequestClient"]):
        self.client = client

        # not implemented stubber, just until endpoints are implemented
        class NotImplementedStub:
            def __getattr__(self, name:"Any"):
                raise NotImplementedError("Teams is not implemented in hyphen.ai yet")
        self.client = NotImplementedStub

    def create(self, name:str) -> "Team":
        """Create a new team, within the context of the current organization"""
        return self.client.post("api/teams", Team, name=name)

    def read(self, id:str) -> "Team":
        """Read a team"""
        return self.client.get(f"api/teams/{id}", Team)

    def list(self) -> "Team":
        """List all teams"""

        class TeamList(BaseModel):
            data: List[Team]

            def __iter__(self):
                return iter(self.data)

            def __getitem__(self, item):
                return self.data[item]

        return self.client.get("api/teams", TeamList)

class AsyncTeamFactory(TeamFactory):

    async def create(self, name:str) -> "Team":
        """Create a new team"""
        return await self.client.post("api/teams", Team, name=name)

    async def read(self, id:str) -> "Team":
        """Read an team"""
        return await self.client.get(f"api/teams/{id}", Team)

    async def list(self) -> "Team":
        """List all teams"""

        class TeamList(BaseModel):
            data: List[Team]

            def __iter__(self):
                return iter(self.data)

            def __getitem__(self, item):
                return self.data[item]

        return await self.client.get("api/teams", TeamList)