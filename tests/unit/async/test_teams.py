import pytest_asyncio
from pytest import mark as m
from pytest import raises

from hyphen import HyphenClient
from hyphen.exceptions import HyphenApiException

NORMAL_MEMBER_ID = "65dfd847846e0004123c6899"

class TestTeamsAsync:

    @pytest_asyncio.fixture
    async def owner_client(self, client_args):
        return HyphenClient(
            async_=True,
            **client_args)

    @pytest_asyncio.fixture
    async def normal_client(self, client_args):
        client_args["impersonate_id"] = NORMAL_MEMBER_ID
        return HyphenClient(
            async_=True,
            **client_args)

    @m.vcr()
    async def test_add_team(self, owner_client):
        name = "Red Team"
        team = await owner_client.teams.create(name=name)
        assert team.name == name
        assert team.id is not None

        teams = await owner_client.teams.list()
        assert team.id in [x.id for x in teams]

    @m.vcr()
    async def test_remove_team(self, owner_client):
        teams = await owner_client.teams.list()
        marketing = [x for x in teams if x.name == "marketing"][0]
        await owner_client.teams.delete(marketing)
        teams = await owner_client.teams.list()
        assert marketing.id not in [x.id for x in teams]


    #@m.vcr()
    async def test_add_team_role(self, owner_client, normal_client):
        teams = await owner_client.teams.list()
        marketing = [x for x in teams if x.name == "marketing"][0]
        normal_member = await owner_client.members.read(NORMAL_MEMBER_ID)
        new_member = await owner_client.members.create(first_name="New", last_name="Member")

        with raises(HyphenApiException):
            normal_marketing = await normal_client.teams.read(marketing.id)
            await normal_marketing.members.add(new_member)

        _ = await marketing.members.assign_role("teamLead", [normal_member])
        normal_marketing = await normal_client.teams.read(marketing.id)
        await normal_marketing.members.add(new_member)
        assert new_member.id in [x.id for x in await marketing.members.list()]