from typing import TYPE_CHECKING, Optional, Union, List
from pydantic import Field, field_validator

from hyphen.base_object import RESTModel
from hyphen.base_factory import BaseFactory
from hyphen.exceptions import IncorrectMethodException

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

    def __repr__(self):
        return f"<Member: {self.first_name} {self.last_name}>"


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
