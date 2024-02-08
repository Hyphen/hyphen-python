from pydantic import AnyHttpUrl, BaseModel, ValidationError
import httpx
from typing import Optional, Union, AsyncGenerator, Generator, TYPE_CHECKING

from hyphen.loggers.hyphen_logger import get_logger
from hyphen.exceptions import AuthenticationException, HyphenApiException

from hyphen.member import MemberFactory, AsyncMemberFactory
from hyphen.movie_quote import MovieQuoteFactory, AsyncMovieQuoteFactory
from hyphen.organization import OrganizationFactory, AsyncOrganizationFactory
from hyphen.team import TeamFactory, AsyncTeamFactory

if TYPE_CHECKING:
    from hyphen.base_object import RESTModel

def logger(level:Optional[str]=None):
    # deal with circular import
    return get_logger(__name__, level=level)

class HyphenClient:
    """The primary interface for working with the Hyphen Engine API.

    ## General Usage
    All interactions with the different Hyphen objects are via a `HyphenClient` instance.
    The client handles auth and scoping, and it provides access to the various object factories for CRUD operations.
    To create a new team, for example, you would use the `team` factory on the client like this:

    Example:

        # sync
        from hyphen import HyphenClient
        client = HyphenClient(client_id="my_client_id", client_secret="my_client_secret")
        new_team = client.team.create("My New Team")

        # async
        from hyphen import HyphenClient
        client = HyphenClient(client_id="my_client_id", client_secret="my_client_secret", async_=True)
        new_team = await client.team.create("My New Team")

    This will generate a new team within the organization associated with the client's credentials.

    Args:
        host: The base URL for the Hyphen api, defaults to https://engine.hyphen.ai
        client_id: The client id for m2m authentication
        client_secret: The client secret used for m2m authentication
        impersonate_id: The id of the user to impersonate, used for "on behalf of" authentication
        organization_id: The id of the organization to act within. Used when more than one organization is available to the credentials or the impersonated user.
        debug: if True, the client will log debug messages
        async_: if True returns an async client
        legacy_api_key: Generally unsupported.

    """
    client: Union["HTTPRequestClient", "AsyncHTTPRequestClient"]
    organization_id: Optional[str]


    @classmethod
    def helloworld(cls) -> str:
        return "Hello World!"

    def __init__(self,
                 host: Optional[AnyHttpUrl]=None,
                 legacy_api_key: Optional[str]=None,
                 client_id: Optional[str]=None,
                 client_secret: Optional[str]=None,
                 impersonate_id: Optional[str]=None,
                 organization_id: Optional[str]=None,
                 debug: Optional[bool]=False,
                 async_:Optional[bool]=False,) -> str:

        self.logger = logger(**{"level": "DEBUG" if debug else None})
        self.host = httpx.URL(str(host)) or "https://engine.hyphen.ai"
        self.organization_id = organization_id
        self.logger.debug("Creating %s HyphenClient...", "async" if async_ else "sync")
        client_args = {
            "hyphen_client": self,
            "host":self.host,
            "legacy_api_key":legacy_api_key,
            "client_id":client_id,
            "client_secret":client_secret,
            "impersonate_id":impersonate_id,
            "debug":debug
        }
        if async_:
            # IMPORTANT: organization must be the first object imported!
            self.client = AsyncHTTPRequestClient(**client_args)
            self.organization = AsyncOrganizationFactory(self.client)

            ## dependent factories ##
            self.member = AsyncMemberFactory(self.client)
            self.movie_quote = AsyncMovieQuoteFactory(self.client)
            self.team = AsyncTeamFactory(self.client)
            self.logger.debug("Async client created.")
            return
        # IMPORTANT: organization must be the first object imported!
        self.client = HTTPRequestClient(**client_args)
        self.organization = OrganizationFactory(self.client)

        ## dependent factories ##
        self.member = MemberFactory(self.client)
        self.movie_quote = MovieQuoteFactory(self.client)
        self.team = TeamFactory(self.client)
        self.logger.debug("Client created.")

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
    host: "httpx.URL"
    hyphen_client: "HyphenClient"
    client: "Generator[httpx.Client]"
    headers:dict = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    def __init__(self,
                 hyphen_client: "HyphenClient",
                 host: Optional[AnyHttpUrl]=None,
                 legacy_api_key: Optional[str]=None,
                 client_id: Optional[str]=None,
                 client_secret: Optional[str]=None,
                 impersonate_id: Optional[str]=None,
                 debug: Optional[bool]=False,
                 timeout: Optional[float]=5.0):

        self.hyphen_client = hyphen_client
        self.logger = self.hyphen_client.logger
        assert legacy_api_key or (client_id and client_secret), "You must provide either a legacy API key or a client id and secret to authenticate with Hyphen.ai"

        if legacy_api_key:
            self.logger.debug("Using legacy API key for authentication")
            self.headers["x-api-key"] = legacy_api_key
        else:
            raise NotImplementedError("M2M authentication is not yet supported")
        if impersonate_id:
            self.logger.debug("Impersonating user %s", impersonate_id)
            self.headers["x-impersonate-id"] = impersonate_id
        self._set_client(host, timeout)

    def _set_client(self,host:AnyHttpUrl, timeout:int):
        """allows for opaque connection pooling"""
        self.logger.debug("attaching sync client with host %s and timeout %s and headers set %s", host, timeout, str(self.headers.keys()))
        self.client = httpx.Client(base_url=str(host), headers=self.headers, timeout=timeout)

    def __del__(self):
        self.client.close()

    def healthcheck(self)-> bool:
        with self.client() as api:
            return api.get("/healthcheck").status_code == 200

    def get(self, path:str, model:BaseModel):
        self.logger.debug("getting GET %s", path)
        response = self.client.get(path)
        self.logger.debug("response status code %s", response.status_code)
        if response.status_code in (401, 403,):
            raise AuthenticationException(response.status_code)
        self.logger.debug("generating response model...")
        response_values = response.json()
        if isinstance(response_values, list):
            response_values = {"data": response_values}
        try:
            return model.model_validate(response_values)
        except ValidationError as e:
            self.logger.error("Unexpected response body from Hyphen.ai: %s", response_values)
            raise e

    def post(self, path:str, model:"BaseModel", instance:"RESTModel"):
        instance_json = instance.model_dump_json(exclude_unset=True, by_alias=True)
        response = self.client.post(path, data=instance_json)
        if response.status_code in (401, 403,):
            raise AuthenticationException(response.status_code)
        if round(response.status_code, -2) != 200:
            self.logger.debug(
                "Unexpected response status code from Hyphen.ai: response.status_code=%s, response.text=%s, path=%s, instance=%s",
                response.status_code,
                response.text,
                path,
                instance_json
            )
            raise HyphenApiException(response.status_code, response.text)
        response_values = response.json()
        if isinstance(response_values, list):
            response_values = {"data": response_values}
        try:
            return model.model_validate(response_values)
        except ValidationError as e:
            self.logger.error("Unexpected response body from Hyphen.ai: %s", response_values)
            raise e

class AsyncHTTPRequestClient(HTTPRequestClient):
    client: "AsyncGenerator[httpx.AsyncClient]"

    def _set_client(self,host:AnyHttpUrl, timeout:int):
        """allows for opaque connection pooling"""
        async def get_client():
            async with httpx.AsyncClient(base_url=host, headers=self.headers, timeout=timeout) as client:
                yield client
        self.client = get_client

    async def healthcheck(self)-> bool:
        async with self.client() as api:
            return await api.get("/healthcheck").status_code == 200

    async def get(self, path:str, model:BaseModel):
        self.logger.debug("async getting GET %s", path)
        response = await self.client.get(path)
        self.logger.debug("async response status code %s", response.status_code)
        if response.status_code in (401, 403,):
            raise AuthenticationException(response.status_code)
        self.logger.debug("async generating response model...")
        return model.model_validate_json(response.text)

    async def post(self, path:str, model:BaseModel, **kwargs):
        response = await self.client.post(path, json=kwargs)
        if response.status_code in (401, 403,):
            raise AuthenticationException(response.status_code)
        return model.model_validate_json(response.text)