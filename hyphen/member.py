from typing import TYPE_CHECKING, Optional

from hyphen.base_object import RESTModel
from hyphen.base_factory import BaseFactory

if TYPE_CHECKING:
    from hyphen.client import HTTPRequestClient, AsyncHTTPRequestClient


class Member(RESTModel):
    id: Optional[str] = None
    first_name: str
    last_name: str

class MemberFactory(BaseFactory):
    _object_class = Member

    def __init__(self, client:"HTTPRequestClient"):
        super().__init__(client)
        self.url_path = f"api/organizations/{self.client.hyphen_client.organization_id}/members"

class AsyncMemberFactory(MemberFactory):

    _object_class = Member

    def __init__(self, client:"AsyncHTTPRequestClient"):
        super().__init__(client)
        self.url_path = f"api/organizations/{self.client.hyphen_client.organization_id}/members"
