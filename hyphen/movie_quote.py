from typing import TYPE_CHECKING, Optional, List, Union, Any
from pydantic import BaseModel

if TYPE_CHECKING:
    from hyphen.client import HTTPRequestClient, AsyncHTTPRequestClient


class MovieQuote(BaseModel):
    quote: str

class MovieQuoteFactory:

    def __init__(self, client:Union["HTTPRequestClient","AsyncHTTPRequestClient"]):
        self.client = client

    def get(self) -> "MovieQuote":
        return self.client.get("api/quote", MovieQuote)

class AsyncMovieQuoteFactory(MovieQuoteFactory):

    async def get(self) -> "MovieQuote":
        return await self.client.get("api/quote", MovieQuote)