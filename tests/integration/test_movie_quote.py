from pytest import mark as m
from pytest import raises

from hyphen import HyphenClient
from hyphen.settings import settings

@m.describe("When checking basic functionality with Hyphen.ai")
@m.integration
class TestMovieQuote:

    @m.vcr
    @m.it("should get a movie quote")
    def test_gets_quote(self):
        hyphen = HyphenClient(
            legacy_api_key=settings.legacy_api_key,
            host=settings.development_hyphen_uri)
        quote = hyphen.movie_quote.get()
        assert quote.quote == "Hey, careful, man, there's a beverage here!"