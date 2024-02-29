from typing import TYPE_CHECKING, List, Any
from pydantic import BaseModel
from abc import ABC

if TYPE_CHECKING:
    from hyphen.client import HTTPRequestClient


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

    def __init__(self, client: "HTTPRequestClient"):
        """Initialize the object factory."""
        self.client = client

    def create(self, **kwargs) -> "Any":
        """Create a new object, within the context of the current organization"""

        def _create(**kwargs) -> self._object_class:
            Candidate = self._object_class(**kwargs)
            return self.client.post(self.url_path, self._object_class, Candidate)

        return _create(**kwargs)

    def read(self, id: str) -> "Any":
        """Read an object"""

        def _read(id: str) -> self._object_class:
            return self.client.get(f"{self.url_path}/{id}", self._object_class)

        return _read(id)

    def list(self) -> "CollectionList":
        """List all objects"""

        class HyphenCollection(CollectionList):
            data: List[self._object_class]

        return self.client.get(self.url_path, HyphenCollection)

    def update(self, target: Any) -> "Any":
        """Update an object. Accepts an updated instance
        to persist.
        """

        def _update(target: self._object_class) -> self._object_class:
            return self.client.patch(
                f"{self.url_path}/{target.id}", self._object_class, target
            )

        return _update(target)

    def delete(self, target: Any) -> None:
        """Delete an object"""

        def _delete(target: self._object_class) -> None:
            return self.client.delete(f"{self.url_path}/{target.id}")

        return _delete(target)


class AsyncBaseFactory(BaseFactory):

    _object_class: type
    url_path: str

    async def __init__(self, client: "HTTPRequestClient"):
        """Initialize the object factory."""
        self.client = client

    async def create(self, **kwargs) -> "Any":
        """Create a new object, within the context of the current organization"""

        async def _create(**kwargs) -> self._object_class:
            Candidate = self._object_class(**kwargs)
            return await self.client.post(self.url_path, self._object_class, Candidate)

        return await _create(**kwargs)

    async def read(self, id: str) -> "Any":
        """Read an object"""

        async def _read(id: str) -> self._object_class:
            return await self.client.get(f"{self.url_path}/{id}", self._object_class)

        return await _read(id)

    async def list(self) -> "CollectionList":
        """List all objects"""

        class HyphenCollection(CollectionList):
            data: List[self._object_class]

        return await self.client.get(self.url_path, HyphenCollection)

    async def delete(self, target: Any) -> None:
        """Delete an object"""

        async def _delete(target: self._object_class) -> None:
            return await self.client.delete(f"{self.url_path}/{target.id}")

        return await _delete(target)
