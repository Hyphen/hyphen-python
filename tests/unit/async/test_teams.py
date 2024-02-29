import pytest_asyncio
from pytest import mark as m
from pytest import raises

from hyphen import HyphenClient
from hyphen.exceptions import HyphenApiException

NORMAL_MEMBER_ID = "65dfd847846e0004123c6899"
LEADER_MEMBER_ID = "65dfe4c2846e0004123c68a7"


class TestTeamsAsync:

    @pytest_asyncio.fixture
    async def owner_client(self, client_args):
        return HyphenClient(async_=True, **client_args)

    @pytest_asyncio.fixture
    async def leader_client(self, client_args):
        client_args["impersonate_id"] = LEADER_MEMBER_ID
        return HyphenClient(async_=True, **client_args)

    @pytest_asyncio.fixture
    async def normal_client(self, client_args):
        client_args["impersonate_id"] = NORMAL_MEMBER_ID
        return HyphenClient(async_=True, **client_args)

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

    @m.vcr()
    async def test_add_team_role(self, owner_client, normal_client):
        teams = await owner_client.teams.list()
        marketing = [x for x in teams if x.name == "marketing"][0]
        normal_member = await owner_client.members.read(NORMAL_MEMBER_ID)
        new_member = await owner_client.members.create(
            first_name="New", last_name="Member"
        )

        with raises(HyphenApiException):
            normal_marketing = await normal_client.teams.read(marketing.id)
            await normal_marketing.members.add(new_member)

        _ = await marketing.members.assign_role("teamLead", [normal_member])
        normal_marketing = await normal_client.teams.read(marketing.id)
        await normal_marketing.members.add(new_member)
        assert new_member.id in [x.id for x in await marketing.members.list()]

    @m.vcr()
    async def test_revoke_team_role(self, owner_client, leader_client, normal_client):
        normal_member = await owner_client.members.read(NORMAL_MEMBER_ID)
        lead_member = await owner_client.members.read(LEADER_MEMBER_ID)

        # lead makes normal a lead
        lead_marketing = [
            x for x in await leader_client.teams.list() if x.name == "marketing"
        ][0]
        normal_member, *_ = await lead_marketing.members.assign_role(
            "teamLead", [normal_member]
        )

        # check that normal is a lead
        assert "teamLead" in [x.name for x in normal_member.roles]
        assert normal_member.roles_context == "team"

        # owner revokes leaders' lead role
        owner_marketing = await owner_client.teams.read(lead_marketing.id)
        _ = await owner_marketing.members.revoke_role("teamLead", lead_member)
        lead_member = [
            x for x in await owner_marketing.members.list() if x.id == lead_member.id
        ][0]

        # check that leader is no longer a lead
        assert "teamLead" not in [x.name for x in lead_member.roles]
        assert lead_member.roles_context == "team"

        # sanity check
        with raises(HyphenApiException):
            _ = await lead_marketing.members.add(normal_member)
        with raises(HyphenApiException):
            _ = await lead_marketing.members.assign_role("teamLead", [lead_member])
