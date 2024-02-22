from pydantic import AnyHttpUrl, BaseModel, ValidationError
from datetime import datetime
import httpx
from json.decoder import JSONDecodeError
from typing import Optional, Union, TYPE_CHECKING

from hyphen.loggers.hyphen_logger import get_logger
from hyphen.base_object import RESTModel
from hyphen.exceptions import AuthenticationException, HyphenApiException
from hyphen.auth import Auth
from hyphen.settings import settings

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
                 organization_id: str,
                 host: Optional[AnyHttpUrl]="https://engine.hyphen.ai",
                 legacy_api_key: Optional[str]=None,
                 client_id: Optional[str]=None,
                 client_secret: Optional[str]=None,
                 impersonate_id: Optional[str]=None,
                 debug: Optional[bool]=False,
                 async_:Optional[bool]=False,) -> str:

        self.logger = logger(**{"level": "DEBUG" if debug else None})
        self.host = httpx.URL(str(host))
        self.organization_id = organization_id
        self.logger.debug("Creating %s HyphenClient...", "async" if async_ else "sync")
        client_args = {
            "hyphen_client": self,
            "host":self.host,
            "legacy_api_key":legacy_api_key,
            "client_id":client_id,
            "client_secret":client_secret,
            "impersonate_id":impersonate_id,
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
    def debug_profile(self) -> dict:
        """Returns a dict of the client's current configuration to help with debugging."""
        safe_m2m = None if not self.client._m2m_credentials else ([self.client._m2m_credentials[0], f'{self.client._m2m_credentials[1][:4]}[redacted]{self.client._m2m_credentials[1][-4:]}'])
        auth_header = self.client.client.headers.get("Authorization", None)
        auth_whole = None if not auth_header else str(auth_header)
        authorization = None if not auth_whole else f"{auth_whole[:8]}[redacted]{auth_whole[-4:]}"
        return {
            "http_client": {
                "client_type": self.client.__class__.__name__,
                "auth_token_expires": self.client._auth_token_expires,
                "m2m_credentials": safe_m2m,
                "headers": {k: v for k, v in self.client.client.headers.items() if not k == "authorization"},
                "authorization_header": authorization,

            },
            "host": str(self.host),
            "organization_id": self.organization_id,
            "on_behalf_of": self.client.client.headers.get("x-hyphen-impersonate"),
        }



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
            quote = await self.client.get("api/quote", Quote)
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

    ### Pluralize factory accessors ###
    # because why not make everyone's life easier?
    @property
    def organizations(self) -> "OrganizationFactory":
        return self.organization
    @property
    def members(self) -> "MemberFactory":
        return self.member
    @property
    def movie_quotes(self) -> "MovieQuoteFactory":
        return self.movie_quote
    @property
    def teams(self) -> "TeamFactory":
        return self.team


class HTTPRequestClient:
    host: "httpx.URL"
    hyphen_client: "HyphenClient"
    client: Optional["httpx.Client"] = None
    headers:dict = None
    _m2m_credentials: Optional[tuple[str, str]] = None
    _auth_token_expires: Optional[float] = 0.0

    def __init__(self,
                 hyphen_client: "HyphenClient",
                 host: Optional[AnyHttpUrl]=None,
                 legacy_api_key: Optional[str]=None,
                 client_id: Optional[str]=None,
                 client_secret: Optional[str]=None,
                 impersonate_id: Optional[str]=None,
                 timeout: Optional[float]=5.0):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.hyphen_client = hyphen_client
        self.logger = self.hyphen_client.logger
        if (settings.hyphen_client_id and settings.hyphen_client_secret):
            self.logger.debug("Using ENV settings for m2m authentication")
            self._m2m_credentials = (settings.hyphen_client_id, settings.hyphen_client_secret,)
        elif (client_id and client_secret):
            self.logger.debug("Using user provided creds for m2m authentication")
            self._m2m_credentials = (client_id, client_secret,)
        elif legacy_api_key:
            self.logger.debug("Using legacy API key for authentication")
            self.headers["x-api-key"] = legacy_api_key
        else:
            raise NotImplementedError("OAuth is not supported, you must provide m2m or legacy credentials to authenticate with Hyphen.ai.")

        if impersonate_id:
            self.logger.debug("Impersonating user %s", impersonate_id)
            self.headers["x-hyphen-impersonate"] = impersonate_id
        self._set_client(host, timeout)

    def auth_expired(self) -> bool:
        """is the current auth token expired? One minute buffer."""
        # can't be expired if youre not using m2m
        return (self._m2m_credentials and (self._auth_token_expires < (datetime.now().timestamp() + 60)))

    def _refresh_m2m_token(self):
        """refreshes a token if it is expired"""
        self.logger.debug("Refreshing m2m token...")
        client_id, client_secret = self._m2m_credentials
        try:
            del self.client.headers["Authorization"]
        except KeyError:
            pass
        response = self.client.post(
            "/api/auth/m2m",
            json={
                "clientId": client_id,
                "clientSecret": client_secret,
            },
        )
        if response.status_code != 200:
            self.logger.error("Unable to refresh auth token: %s", response.text)
            raise AuthenticationException(response.text)
        auth = Auth.model_validate_json(response.text)
        self._auth_token_expires = auth.expires_at.timestamp()
        self.client.headers["Authorization"] = f"Bearer {auth.access_token}"
        self.logger.debug("M2M token refreshed")


    def _set_client(self,host:AnyHttpUrl, timeout:int):
        """allows for opaque connection pooling"""
        self.logger.debug("attaching sync client with host %s and timeout %s and headers set %s", host, timeout, str(self.headers.keys()))
        self.client = httpx.Client(base_url=str(host), headers=self.headers, timeout=timeout)

    def __del__(self):
        if self.client:
            self.client.close()

    def healthcheck(self)-> bool:
        if self.auth_expired():
            self._refresh_m2m_token()
        return self.client.get("/healthcheck").status_code == 200

    def get(self, path:str, model:"RESTModel"):
        self.logger.debug("GET %s", path)
        if self.auth_expired():
            self._refresh_m2m_token()
        response = self.client.get(path)
        handled = self._handle_response(response, path=path, model=model)
        self.logger.debug("GET response complete: %s", handled)
        return handled

    def post(self, path:str, model:"BaseModel", instance:"RESTModel"):
        self.logger.debug("POST %s", path)
        if self.auth_expired():
            self._refresh_m2m_token()
        instance_json = instance.model_dump_json(exclude_unset=True, by_alias=True)
        response = self.client.post(path, data=instance_json)
        handled = self._handle_response(response, path, model, instance)
        self.logger.debug("POST response complete: %s", handled)
        return handled

    def put(self,
            path:str,
            model:Optional["BaseModel"]=None,
            instance:Optional["RESTModel"]=None):
        self.logger.debug("PUT %s", path)
        instance_json = instance.model_dump_json(exclude_unset=True, by_alias=True)
        if self.auth_expired():
            self._refresh_m2m_token()
        response = self.client.put(path, data=instance_json)
        handled = self._handle_response(response, path=path, model=model, instance=instance)
        self.logger.debug("PUT response complete: %s", handled)
        return handled

    def patch(self,
            path:str,
            model:"BaseModel",
            instance:"RESTModel"):
        self.logger.debug("PATCH %s", path)
        instance_json = instance.model_dump_json(exclude_unset=True, by_alias=True, exclude=("id",))
        if self.auth_expired():
            self._refresh_m2m_token()
        response = self.client.patch(path, data=instance_json)
        handled = self._handle_response(response, path=path, model=model, instance=instance)
        self.logger.debug("PATCH response complete: %s", handled)
        return handled

    def delete(self, path:str):
        self.logger.debug("DELETE %s", path)
        if self.auth_expired():
            self._refresh_m2m_token()
        response = self.client.delete(path)
        handled = self._handle_response(response, path=path)
        self.logger.debug("DELETE response complete: %s", handled)
        return handled

    def _handle_response(self,
                        response:"httpx.Response",
                        path:Optional[str]=None,
                        model:Optional["RESTModel"]=None,
                        instance:Optional["RESTModel"]=None):
        if response.status_code in (401, 403,):
            raise AuthenticationException(response.status_code)
        if round(response.status_code, -2) != 200:
            self.logger.debug(
                "Unexpected response status code from Hyphen.ai: response.status_code=%s, response.text=%s, path=%s, instance=%s",
                response.status_code,
                response.text,
                path,
                instance,
            )
            raise HyphenApiException(response.status_code, response.text)
        self.logger.debug("generating response model...")
        if not all((response.text, model,)):
            self.logger.debug("No response body or model to validate, returning None")
            return None
        self.logger.debug("Parsing api response json...")
        try:
            response_values = response.json()
        except JSONDecodeError as e:
            self.logger.error("Unexpected response body from Hyphen.ai that could not be decoded as valid json: %s", response.text)
            raise e
        except Exception as e:
            self.logger.error("Another, unknown error occurred while parsing response body from Hyphen.ai: %s, %s", response.text, e)
            raise e
        try:
            self.logger.debug("parsing response into %s instance...", model.__name__)
            parsed = model.model_validate(response_values)
            self.logger.debug("Parsed model %s returned", parsed)
            return parsed
        except ValidationError as e:
            self.logger.error("Unable to parse: unexpected response body from Hyphen.ai: %s", response_values)
            raise e



class AsyncHTTPRequestClient(HTTPRequestClient):
    client: Optional["httpx.AsyncClient"] = None

    def _set_client(self,host:AnyHttpUrl, timeout:int):
        """allows for opaque connection pooling"""
        self.client = httpx.AsyncClient(base_url=host, headers=self.headers, timeout=timeout)

    async def _refresh_m2m_token(self):
        """refreshes a token if it is expired"""
        self.logger.debug("Refreshing m2m token...")
        client_id, client_secret = self._m2m_credentials
        try:
            del self.client.headers["Authorization"]
        except KeyError:
            pass
        response = await self.client.post(
            "/api/auth/m2m",
            json={
                "clientId": client_id,
                "clientSecret": client_secret,
            },
        )
        if response.status_code != 200:
            self.logger.error("Unable to refresh auth token: %s", response.text)
            raise AuthenticationException(response.text)
        auth = Auth.model_validate_json(response.text)
        self._auth_token_expires = auth.expires_at.timestamp()
        self.client.headers["Authorization"] = f"Bearer {auth.access_token}"
        self.logger.debug("M2M token refreshed")

    async def healthcheck(self)-> bool:
        if self.auth_expired():
            await self._refresh_m2m_token()
        return await self.client.get("/healthcheck").status_code == 200

    async def get(self, path:str, model:"RESTModel"):
        self.logger.debug("getting GET %s", path)
        if self.auth_expired():
            await self._refresh_m2m_token()
        response = await self.client.get(path)
        return self._handle_response(response, path=path, model=model)

    async def post(self, path:str, model:"BaseModel", instance:"RESTModel"):
        instance_json = instance.model_dump_json(exclude_unset=True, by_alias=True)
        if self.auth_expired():
            await self._refresh_m2m_token()
        response = await self.client.post(path, data=instance_json)
        return self._handle_response(response, path, model, instance)

    async def put(self,
            path:str,
            model:Optional["BaseModel"]=None,
            instance:Optional["RESTModel"]=None):
        instance_json = instance.model_dump_json(exclude_unset=True, by_alias=True)
        if self.auth_expired():
            await self._refresh_m2m_token()
        response = await self.client.put(path, data=instance_json)
        return self._handle_response(response, path=path, model=model, instance=instance)

    async def delete(self, path:str):
        self.logger.debug("DELETE %s", path)
        if self.auth_expired():
            await self._refresh_m2m_token()
        response = await self.client.delete(path)
        handled = self._handle_response(response, path=path)
        self.logger.debug("DELETE response complete: %s", handled)
        return handled

    async def patch(self,
            path:str,
            model:"BaseModel",
            instance:"RESTModel"):
        self.logger.debug("PATCH %s", path)
        instance_json = instance.model_dump_json(exclude_unset=True, by_alias=True, exclude=("id",))
        if self.auth_expired():
            await self._refresh_m2m_token()
        response = await self.client.patch(path, data=instance_json)
        handled = self._handle_response(response, path=path, model=model, instance=instance)
        self.logger.debug("PATCH response complete: %s", handled)
        return handled

    async def __del__(self):
        if self.client:
            await self.client.aclose()