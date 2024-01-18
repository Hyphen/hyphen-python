from pydantic import AnyHttpUrl
from typing import Optional

class HyphenClient:
    """The primary interface for working with the Hyphen Engine API.
    Args:
        host: The base URL for the Hyphen api, defaults to our production https://engine.hyphen.ai
        legacy_api_key: Generally unsupported, but can be used for local development
        client_id: The client id for m2m authentication
        client_secret: The client secret used for m2m authentication
    """

    @classmethod
    def helloworld(cls) -> str:
        return "Hello World!"

    def __init__(self,
                 host: Optional[AnyHttpUrl]=None,
                 legacy_api_key: Optional[str]=None,
                 client_id: Optional[str]=None,
                 client_secret: Optional[str]=None,) -> str:
        assert legacy_api_key or (client_id and client_secret), "You must provide either a legacy API key or a client id and secret to authenticate with Hyphen.ai"

        self.host = host or "https://engine.hyphen.ai"

    @property
    def authenticated(self) -> bool:
        """Returns true if the client is authenticated, false otherwise"""
        return False


