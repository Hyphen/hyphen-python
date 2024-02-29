from typing import TYPE_CHECKING, Optional, List
from pydantic import BaseModel

from hyphen.base_factory import BaseFactory, CollectionList
from hyphen.member import MemberFactory, AsyncMemberFactory

if TYPE_CHECKING:
    from hyphen.client import HTTPRequestClient


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

    def __init__(self, client: "HTTPRequestClient"):
        super().__init__(client)
        self.url_path = (
            f"api/organizations/{self.client.hyphen_client.organization_id}/teams"
        )

    def create(self, name: str) -> "Team":  # noqa pylint: disable=arguments-differ
        """Create a new team"""
        instance = Team(name=name)
        created = self.client.post(self.url_path, Team, instance)
        return self._add_member_factory(created)

    def read(self, id: str) -> "Team":  # noqa pylint: redefined-builtin
        """Read an existing team"""
        team = super().read(id)
        return self._add_member_factory(team)  # noqa pylint: protected-access

    def list(self) -> "Team":
        """List all teams available with the provided credentials."""

        class HyphenCollection(CollectionList):
            data: List[Team]

        collection = self.client.get(self.url_path, HyphenCollection)
        updated_collection = []
        for team in collection:
            updated_collection.append(
                self._add_member_factory(team)
            )  # noqa pylint: protected-access
        return updated_collection

    def update(self, target: "Team") -> "Team":
        """Update an existing team"""
        team = super().update(target)
        return self._add_member_factory(team)  # noqa pylint: protected-access

    def _add_member_factory(self, team: "Team") -> "Team":
        if self.__class__.__name__ == "AsyncTeamFactory":
            team._member_factory = AsyncMemberFactory(  # noqa pylint: protected-access
                self.client
            )
        else:
            team._member_factory = MemberFactory(  # noqa pylint: protected-access
                self.client
            )
        team._member_factory.url_path = (  # noqa pylint: protected-access
            f"{self.url_path}/{team.id}/members"
        )
        return team


class AsyncTeamFactory(TeamFactory):

    async def create(self, name: str) -> "Team":
        """Create a new team"""
        instance = Team(name=name)
        created = await self.client.post(self.url_path, Team, instance)
        return self._add_member_factory(created)

    async def read(self, id: str) -> "Team":  # noqa pylint: redefined-builtin
        """Read an existing team"""
        team = await self.client.get(f"{self.url_path}/{id}", Team)
        return self._add_member_factory(team)

    async def list(self) -> "Team":
        """List all teams available with the provided credentials."""

        class HyphenCollection(CollectionList):
            data: List[Team]

        collection = await self.client.get(self.url_path, HyphenCollection)
        updated_collection = []
        for team in collection:
            updated_collection.append(self._add_member_factory(team))
        return updated_collection

    async def update(self, target: "Team") -> "Team":
        """Update an existing team"""
        team = super().update(target)
        return await self._add_member_factory(team)
