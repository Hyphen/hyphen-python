from pydantic import AnyHttpUrl, BaseModel
import httpx
from typing import Optional

from hyphen.loggers.hyphen_logger import get_logger
from hyphen.exceptions import AuthenticationException

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
    client: "HTTPRequestClient"


    @classmethod
    def helloworld(cls) -> str:
        return "Hello World!"

    def __init__(self,
                 host: Optional[AnyHttpUrl]=None,
                 legacy_api_key: Optional[str]=None,
                 client_id: Optional[str]=None,
                 client_secret: Optional[str]=None,) -> str:

        self.logger = logger()
        self.host = httpx.URL(str(host)) or "https://engine.hyphen.ai"

        self.client = HTTPRequestClient(host=self.host,
                                        legacy_api_key=legacy_api_key,
                                        client_id=client_id,
                                        client_secret=client_secret)
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

class HTTPRequestClient:
    host: AnyHttpUrl
    sync_client: httpx.Client
    headers:dict = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    def __init__(self,
                 host: Optional[AnyHttpUrl]=None,
                 legacy_api_key: Optional[str]=None,
                 client_id: Optional[str]=None,
                 client_secret: Optional[str]=None,):
        self.logger = logger()
        assert legacy_api_key or (client_id and client_secret), "You must provide either a legacy API key or a client id and secret to authenticate with Hyphen.ai"

        if legacy_api_key:
            self.logger.debug("Using legacy API key for authentication")
            self.headers["x-api-key"] = legacy_api_key
        else:
            raise NotImplementedError("M2M authentication is not yet supported")
        self.client = httpx.Client(base_url=host, headers=self.headers)

    def healthcheck(self)-> bool:
        return self.client.get(f"{self.host}/healthcheck").status_code == 200

    def get(self, path:str, model:BaseModel):
        with self.client as api:
            response = api.get(path)
        if response.status_code in (401, 403,):
            raise AuthenticationException(response.status_code)
        return model.model_validate_json(response.text)