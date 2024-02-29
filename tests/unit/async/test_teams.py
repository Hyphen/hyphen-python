import pytest_asyncio
from pytest import mark as m

from hyphen import HyphenClient


class TestTeamsAsync:

    @pytest_asyncio.fixture
    async def client(self, client_args):
        return HyphenClient(
            async_=True,
            **client_args)


    @m.vcr()
    async def test_add_team(self, client):
        name = "Red Team"
        team = await client.teams.create(name=name)
        assert team.name == name
        assert team.id is not None

        teams = await client.teams.list()
        assert team.id in [x.id for x in teams]

    @m.vcr()
    async def test_remove_team(self, client):
        teams = await client.teams.list()
        marketing = [x for x in teams if x.name == "marketing"][0]
        await client.teams.delete(marketing)
        teams = await client.teams.list()
        assert marketing.id not in [x.id for x in teams]
