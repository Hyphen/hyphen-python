from typing import TYPE_CHECKING, List, Any
from pydantic import BaseModel
from abc import ABC

from hyphen.exceptions import AmbiguousOrganizationException

if TYPE_CHECKING:
    from hyphen.client import HTTPRequestClient, AsyncHTTPRequestClient




class CollectionList(BaseModel):
    data: List[Any]

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, item):
        return self.data[item]


class BaseFactory(ABC):
    """The common ancestor of all object factories"""
    _object_class: type
    url_path: str

    def __init__(self, client:"HTTPRequestClient"):
        """Initialize the object factory.

        Note: The first time any object is initilized it will check to see if `hyphen_client.organization_id` is set.
            If it is not, the factory will attempt to set it by polling Hyphen.ai for the organization associated with the credentials.
            This is required because most operations must be scoped to an Organization.
        """
        self.client = client
        if self.client.hyphen_client.organization_id is None:
            authorized_orgnaizations = self.client.hyphen_client.organization.list()
            org_count = len(authorized_orgnaizations.data)
            if org_count != 1:
                raise AmbiguousOrganizationException(("Attempt to implicitly determine organization for given credentials failed. "
                                                      f"Hyphen.ai returned {org_count} organizations authorized by these credentails."))
            self.client.hyphen_client.organization_id = self.client.hyphen_client.organization.list()[0].id

    def create(self, **kwargs) -> "Any":
        f"""Create a new {str(self._object_class)}, within the context of the current organization"""
        def _create(**kwargs) -> self._object_class:
            Candidate = self._object_class(**kwargs)
            return self.client.post(self.url_path, self._object_class, Candidate)
        return _create(**kwargs)

    def read(self, id:str) -> "Any":
        f"""Read a {self._object_class}"""
        def _read(id:str) -> self._object_class:
            return self.client.get(f"{self.url_path}/{id}", self._object_class)
        return _read(id)

    def list(self) -> "CollectionList":
        """List all {self._object_class}s"""
        class HyphenCollection(CollectionList):
            data: List[self._object_class]

        return self.client.get(self.url_path, HyphenCollection)

    def delete(self, id:str) -> None:
        f"""Delete a {self._object_class}"""
        return self.client.delete(f"{self.url_path}/{id}")


class AsyncBaseFactory(BaseFactory):

    _object_class: type
    url_path: str

    async def __init__(self, client: "AsyncHTTPRequestClient"):
        """Initialize the object factory.

        Note: The first time any object is initilized it will check to see if `hyphen_client.organization_id` is set.
            If it is not, the factory will attempt to set it by polling Hyphen.ai for the organization associated with the credentials.
            This is required because most operations must be scoped to an Organization.
        """
        self.client = client
        if self.client.hyphen_client.organization_id is None:
            authorized_orgnaizations = await self.client.hyphen_client.organization.list()
            org_count = len(authorized_orgnaizations.data)
            if org_count != 1:
                raise AmbiguousOrganizationException(("Attempt to implicitly determine organization for given credentials failed. "
                                                      f"Hyphen.ai returned {org_count} organizations authorized by these credentails."))
            self.client.hyphen_client.organization_id = self.client.hyphen_client.organization.list()[0].id

    async def create(self, name:str) -> "Any":
        f"""Create a new {str(self._object_class)}, within the context of the current organization"""
        async def _create(name:str) -> self._object_class:
            return await self.client.post(self.url_path, self._object_class, name=name)
        return await _create(name)

    async def read(self, id:str) -> "Any":
        f"""Read a {self._object_class}"""
        async def _read(id:str) -> self._object_class:
            return await self.client.get(f"{self.url_path}/{id}", self._object_class)
        return await _read(id)

    async def list(self) -> "CollectionList":
        """List all {self._object_class}s"""
        return await self.client.get(self.url_path, CollectionList)