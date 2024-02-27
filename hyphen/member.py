from typing import TYPE_CHECKING, Optional, Union, List, Literal
from pydantic import Field, field_validator

from hyphen.base_object import RESTModel
from hyphen.base_factory import BaseFactory
from hyphen.exceptions import IncorrectMethodException
from hyphen.roles import Role, LocalizedRole

from hyphen.connected_accounts.slack import Slack

if TYPE_CHECKING:
    from hyphen.client import HTTPRequestClient, AsyncHTTPRequestClient
    from hyphen.team import Team
    from hyphen.organization import Organization

class MemberIdsReference(RESTModel):
    members: List[dict]

    @field_validator("members", mode="before")
    @classmethod
    def convert_member_object(cls, value:"Member"):
        members = []
        for member in value:
            member_id = getattr(member, "id", None)
            member_roles = [role.name for role in getattr(member, "roles", [])]
            members.append({"id": member_id, "roles": member_roles})
        return members

class Member(RESTModel):
    id: Optional[str] = None
    first_name: str
    last_name: str
    connected_accounts: Optional[List[Union[Slack, dict]]] = []
    roles: List[Optional[Role]] = []
    roles_context: Literal["organization", "team"] = Field(default=None, exclude=True)


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

    def update_context(self, context:Union["Team", "Organization"]):
        return context.member.get(self.id)

class MemberFactory(BaseFactory):
    _object_class = Member

    def __init__(self, client:"HTTPRequestClient"):
        super().__init__(client)
        self.url_path = f"api/organizations/{self.client.hyphen_client.organization_id}/members"

    def list(self) -> List[Member]:
        """List all members available with the provided credentials.
        """
        members = super().list()
        return [self._scope_member(member) for member in members]

    def add(self, member: Member) -> None:
        """Add a member to the team"""
        if "team" not in self.url_path:
            raise IncorrectMethodException("To add a Member to an Organization, use `client.member.create()`. To add a Member to a Team, use `team.member.add()`.")

        member = self.client.put(self.url_path,
                                 instance=MemberIdsReference(members=[member]))
        return self._scope_member(member)

    def remove(self, member: "Member") -> None:
        """Remove a member from the team"""
        if "team" not in self.url_path:
            raise IncorrectMethodException("To delete a Member from an Organization, use `client.member.delete()`. To remove a Member from a Team, use `team.member.remove()`.")
        return self.client.delete(f"{self.url_path}/{member.id}")

    def assign_role(self, role_name: str, members:List[Member]) -> None:
        """Assign a role to a member for either a team or an organization."""
        members = self._apply_role_to_members(role_name, members)

        # TODO: should verify the response object
        _ = self.client.put(f"{self.url_path}",
                             instance=MemberIdsReference(members=members))
        return [self._scope_member(member) for member in members]

    def revoke_role(self, role: Union[Role, str], member: Member) -> None:
        """Remove a role from a member for either a team or an organization.
        Note: since this is not a bulk operation in the api we can't safely enforce ACID
        transactions, so this method only supports one call at a time.
        """
        if self.role_context == "organization":
            raise NotImplementedError("Revoking roles from an organization is not yet supported.")

        role_name = getattr(role, "name", role)
        return self.client.delete(f"{self.url_path}/{member.id}/roles", LocalizedRole(roles=[role_name]))

    @property
    def role_context_id(self) -> str:
        return self.url_path.split("/")[-2]

    @property
    def role_context(self) -> str:
        return "team" if "team" in self.url_path else "organization"

    def _scope_member(self, member:"Member") -> List[Role]:
        """Scope roles to the current object"""
        member.roles_context = member.roles_context or self.role_context
        for role in member.roles:
            role.context = role.context or self.role_context
            role.context_id = role.context_id or self.role_context_id
        return member

    def _apply_role_to_members(self, role_name:str, members:List[Member]) -> List[Member]:
        """Apply a role to a member"""
        role = Role(name=role_name,
                    context=self.role_context,
                    context_id=self.role_context_id)
        for member in members:
            if role not in member.roles:
                member.roles.append(role)
        return members

class AsyncMemberFactory(MemberFactory):

    _object_class = Member

    def __init__(self, client:"AsyncHTTPRequestClient"):
        super().__init__(client)
        self.url_path = f"api/organizations/{self.client.hyphen_client.organization_id}/members"

    async def list(self) -> List[Member]:
        """List all members available with the provided credentials.
        """
        members = await super().list()
        return [self._scope_member(member) for member in members]

    async def add(self, member: Union["Member",str]) -> None:
        """Add a member to the team"""
        if "team" not in self.url_path:
            raise IncorrectMethodException("To add a Member to an Organization, use `client.member.create()`. To add a Member to a Team, use `team.member.add()`.")

        member = await self.client.put(self.url_path,
                               instance=MemberIdsReference(member_ids=member))
        return self._scope_member(member)

    async def remove(self, member: Union["Member"]) -> None:
        """Remove a member from the team"""
        if "team" not in self.url_path:
            raise IncorrectMethodException("To delete a Member from an Organization, use `client.member.delete()`. To remove a Member from a Team, use `team.member.remove()`.")
        return await self.client.delete(f"{self.url_path}/{member.id}")

    async def assign_role(self, role_name: str, members:List[Member]) -> None:
        """Assign a role to a member for either a team or an organization."""
        members = self._apply_role_to_members(role_name, members)

        # TODO: should verify the response object
        _ = await self.client.put(f"{self.url_path}",
                             instance=MemberIdsReference(members=members))
        return [self._scope_member(member) for member in members]

    async def revoke_role(self, role: Union[Role, str], member: Member) -> None:
        if self.role_context == "organization":
            raise NotImplementedError("Revoking roles from an organization is not yet supported.")

        role_name = getattr(role, "name", role)
        return await self.client.delete(f"{self.url_path}/{member.id}/roles", LocalizedRole(roles=[role_name]))