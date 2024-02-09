from typing import TYPE_CHECKING, Optional, Union, List
from pydantic import Field, field_validator

from hyphen.base_object import RESTModel
from hyphen.base_factory import BaseFactory
from hyphen.exceptions import IncorrectMethodException

from hyphen.connected_accounts.slack import Slack

if TYPE_CHECKING:
    from hyphen.client import HTTPRequestClient, AsyncHTTPRequestClient

class MemberIdsReference(RESTModel):
    member_ids: List[str]

    @field_validator("member_ids", mode="before")
    @classmethod
    def convert_member_object(cls, value:Union["Member",str]):
        member_id = getattr(value, "id", value)
        return [member_id]

class Member(RESTModel):
    id: Optional[str] = None
    first_name: str
    last_name: str
    connected_accounts: Optional[List[Union[Slack, dict]]] = []

    def __repr__(self):
        return f"<Member: {self.first_name} {self.last_name}>"

    @field_validator("connected_accounts", mode="before")
    @classmethod
    def parse_connected_accounts(cls, value:List) -> List[Union[Slack, dict]]:
        if not value:
            return []
        parsed_accounts = []
        for account in value:
            if isinstance(account, Slack):
                parsed_accounts.append(account)
                continue
            if account.get("type", None) == "slack":
                parsed_accounts.append(Slack(**account))
                continue
            parsed_accounts.append(account)
        return parsed_accounts

    @property
    def slack(self) -> Optional[Slack]:
        for account in self.connected_accounts:
            if isinstance(account, Slack):
                return account
        return None

class MemberFactory(BaseFactory):
    _object_class = Member

    def __init__(self, client:"HTTPRequestClient"):
        super().__init__(client)
        self.url_path = f"api/organizations/{self.client.hyphen_client.organization_id}/members"

    def add(self, member: Union["Member",str]) -> None:
        """Add a member to the team"""
        if "team" not in self.url_path:
            raise IncorrectMethodException("To add a Member to an Organization, use `client.member.create()`. To add a Member to a Team, use `team.member.add()`.")

        return self.client.put(self.url_path,
                               instance=MemberIdsReference(member_ids=member))

    def remove(self, member: Union["Member",str]) -> None:
        """Remove a member from the team"""
        if "team" not in self.url_path:
            raise IncorrectMethodException("To delete a Member from an Organization, use `client.member.delete()`. To remove a Member from a Team, use `team.member.remove()`.")
        return self.client.delete(self.url_path,
                                  instance=MemberIdsReference(member_ids=member))

class AsyncMemberFactory(MemberFactory):

    _object_class = Member

    def __init__(self, client:"AsyncHTTPRequestClient"):
        super().__init__(client)
        self.url_path = f"api/organizations/{self.client.hyphen_client.organization_id}/members"

    async def add(self, member: Union["Member",str]) -> None:
        """Add a member to the team"""
        if "team" not in self.url_path:
            raise IncorrectMethodException("To add a Member to an Organization, use `client.member.create()`. To add a Member to a Team, use `team.member.add()`.")

        return await self.client.put(self.url_path,
                               instance=MemberIdsReference(member_ids=member))

    async def remove(self, member: Union["Member",str]) -> None:
        """Remove a member from the team"""
        if "team" not in self.url_path:
            raise IncorrectMethodException("To delete a Member from an Organization, use `client.member.delete()`. To remove a Member from a Team, use `team.member.remove()`.")
        return await self.client.delete(self.url_path,
                                  instance=MemberIdsReference(member_ids=member))