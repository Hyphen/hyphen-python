import pytest_asyncio
from pytest import mark as m
from faker import Faker

fake = Faker()
from hyphen import HyphenClient


class TestTeamsAsync:

    @pytest_asyncio.fixture
    async def client(self, client_args):
        return HyphenClient(
            async_=True,
            **client_args)


    @m.vcr()
    async def test_add_team(self, client):
        name = fake.company()
        team = await client.teams.create(name=name)
        assert team.name == name
        assert team.id is not None

        teams = await client.teams.list()
        assert team.id in [x.id for x in teams]


