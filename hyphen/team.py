from typing import TYPE_CHECKING, Optional, List
from pydantic import BaseModel

from hyphen.base_factory import BaseFactory, CollectionList
from hyphen.member import MemberFactory

if TYPE_CHECKING:
    from hyphen.client import HTTPRequestClient, AsyncHTTPRequestClient


class Team(BaseModel):
    id: Optional[str] = None
    name: str

    _member_factory: Optional["MemberFactory"] = None

    @property
    def member(self) -> "MemberFactory":
        return self._member_factory

    @property
    def members(self) -> "MemberFactory":
        """allow both forms for a better Developer experience"""
        return self._member_factory

class TeamFactory(BaseFactory):
    _object_class = Team

    def __init__(self, client:"HTTPRequestClient"):
        super().__init__(client)
        self.url_path = f"api/organizations/{self.client.hyphen_client.organization_id}/teams"

    def create(self, name:str) -> "Team":
        """Create a new team"""
        instance = Team(name=name)
        created = self.client.post(self.url_path, Team, instance)
        return self._add_member_factory(created)

    def list(self) -> "Team":
        """List all teams available with the provided credentials.
        """
        class HyphenCollection(CollectionList):
            data: List[Team]

        collection = self.client.get(self.url_path, HyphenCollection)
        updated_collection = []
        for team in collection:
            updated_collection.append(self._add_member_factory(team))
        return updated_collection

    def update(self, target:"Team") -> "Team":
        """Update an existing team"""
        team = super().update(target)
        return self._add_member_factory(team)

    def _add_member_factory(self, team:"Team") -> "Team":
        team._member_factory = MemberFactory(self.client)
        team._member_factory.url_path = f"{self.url_path}/{team.id}/members"
        return team

class AsyncTeamFactory(TeamFactory):

    async def create(self, name:str) -> "Team":
        """Create a new team"""
        instance = Team(name=name)
        created = await self.client.post(self.url_path, Team, instance)
        return self._add_member_factory(created)

    async def list(self) -> "Team":
        """List all teams available with the provided credentials.
        """
        class HyphenCollection(CollectionList):
            data: List[Team]

        collection = await self.client.get(self.url_path, HyphenCollection)
        updated_collection = []
        for team in collection:
            updated_collection.append(self._add_member_factory(team))
        return updated_collection

    async def update(self, target:"Team") -> "Team":
        """Update an existing team"""
        team = super().update(target)
        return await self._add_member_factory(team)