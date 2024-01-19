from pydantic import AnyHttpUrl, BaseModel
import httpx
from typing import Optional, Callable, Union

from hyphen.loggers.hyphen_logger import get_logger
from hyphen.exceptions import AuthenticationException

from hyphen.organization import OrganizationFactory, AsyncOrganizationFactory

def logger():
    # deal with circular import
    return get_logger(__name__)

class HyphenClient:
    """The primary interface for working with the Hyphen Engine API.
    Args:
        host: The base URL for the Hyphen api, defaults to our production https://engine.hyphen.ai
        legacy_api_key: Generally unsupported, but can be used for local development
        client_id: The client id for m2m authentication
        client_secret: The client secret used for m2m authentication
    """
    client: Union["HTTPRequestClient", "AsyncHTTPRequestClient"]


    @classmethod
    def helloworld(cls) -> str:
        return "Hello World!"

    def __init__(self,
                 host: Optional[AnyHttpUrl]=None,
                 legacy_api_key: Optional[str]=None,
                 client_id: Optional[str]=None,
                 client_secret: Optional[str]=None,
                 async_:Optional[bool]=False,) -> str:

        self.logger = logger()
        self.host = httpx.URL(str(host)) or "https://engine.hyphen.ai"
        logger.debug("Creating %s HyphenClient...", "async" if async_ else "sync")
        if async_:
            self.client = AsyncHTTPRequestClient(host=self.host,
                                            legacy_api_key=legacy_api_key,
                                            client_id=client_id,
                                            client_secret=client_secret)

            self.organization = AsyncOrganizationFactory(self.client)
            logger.debug("Async client created.")
            return
        self.client = HTTPRequestClient(host=self.host,
                                        legacy_api_key=legacy_api_key,
                                        client_id=client_id,
                                        client_secret=client_secret)

        self.organization = OrganizationFactory(self.client)
        logger.debug("Client created.")

    @property
    def authenticated(self) -> bool:
        """Returns true if the client is authenticated, false otherwise"""
        class Quote(BaseModel):
            quote:str

        try:
            quote = self.client.get("api/quote", Quote)
            return quote.quote is not None
        except AuthenticationException as e:
            self.logger.error(e)
            return False
        except AttributeError as e:
            self.logger.error(e)
            raise e

    @property
    async def async_authenticated(self) -> bool:
        """Returns true if the client is authenticated, false otherwise"""
        class Quote(BaseModel):
            quote:str

        try:
            quote = self.client.get("api/quote", Quote)
            return quote.quote is not None
        except AuthenticationException as e:
            self.logger.error(e)
            return False
        except AttributeError as e:
            self.logger.error(e)
            raise e


    def healthcheck(self) -> bool:
        """Returns true if the client is healthy, false otherwise"""
        return self.client.healthcheck()

    async def async_healthcheck(self) -> bool:
        """Returns true if the client is healthy, false otherwise"""
        return await self.client.healthcheck()


class HTTPRequestClient:
    host: AnyHttpUrl
    client: Callable
    sync_client: httpx.Client
    headers:dict = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    def __init__(self,
                 host: Optional[AnyHttpUrl]=None,
                 legacy_api_key: Optional[str]=None,
                 client_id: Optional[str]=None,
                 client_secret: Optional[str]=None,
                 timeout: Optional[float]=5.0):
        self.logger = logger()
        assert legacy_api_key or (client_id and client_secret), "You must provide either a legacy API key or a client id and secret to authenticate with Hyphen.ai"

        if legacy_api_key:
            self.logger.debug("Using legacy API key for authentication")
            self.headers["x-api-key"] = legacy_api_key
        else:
            raise NotImplementedError("M2M authentication is not yet supported")
        self._set_client(host, timeout)

    def _set_client(self,host:AnyHttpUrl, timeout:int):
        self.logger.debug("attaching sync client with host %s and timeout %s and headers set %s", host, timeout, str(self.headers.keys()))
        self.client = lambda : httpx.Client(base_url=str(host), headers=self.headers, timeout=timeout)

    def healthcheck(self)-> bool:
        with self.client() as api:
            return api.get("/healthcheck").status_code == 200

    def get(self, path:str, model:BaseModel):
        self.logger.debug("getting GET %s", path)
        with self.client() as api:
            response = api.get(path)
        self.logger.debug("response status code %s", response.status_code)
        if response.status_code in (401, 403,):
            raise AuthenticationException(response.status_code)
        self.logger.debug("generating response model...")
        return model.model_validate_json(response.text)

    def post(self, path:str, model:BaseModel, **kwargs):
        with self.client() as api:
            response = api.post(path, json=kwargs)
        if response.status_code in (401, 403,):
            raise AuthenticationException(response.status_code)
        return model.model_validate_json(response.text)

class AsyncHTTPRequestClient(HTTPRequestClient):
    sync_client: httpx.AsyncClient


    def _set_client(self,host:AnyHttpUrl, timeout:int):
        self.client = lambda : httpx.AsyncClient(base_url=host, headers=self.headers, timeout=timeout)

    async def healthcheck(self)-> bool:
        async with self.client() as api:
            return await api.get("/healthcheck").status_code == 200

    async def get(self, path:str, model:BaseModel):
        self.logger.debug("async getting GET %s", path)
        async with self.client() as api:
            response = await api.get(path)
        self.logger.debug("async response status code %s", response.status_code)
        if response.status_code in (401, 403,):
            raise AuthenticationException(response.status_code)
        self.logger.debug("async generating response model...")
        return model.model_validate_json(response.text)

    async def post(self, path:str, model:BaseModel, **kwargs):
        async with self.client() as api:
            response = await api.post(path, json=kwargs)
        if response.status_code in (401, 403,):
            raise AuthenticationException(response.status_code)
        return model.model_validate_json(response.text)