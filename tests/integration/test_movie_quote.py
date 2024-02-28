from pytest import mark as m
from pytest import raises

from hyphen import HyphenClient

@m.describe("When checking basic functionality with Hyphen.ai")
@m.integration
class TestMovieQuote:

    @m.vcr
    @m.it("should get a movie quote")
    def test_gets_quote(self, settings):
        hyphen = HyphenClient(
            organization_id="xxxxxxxx-xxxxxxx",
            client_id=settings.test_hyphen_client_id,
            client_secret=settings.test_hyphen_client_secret,
            host=settings.test_hyphen_url,)
        quote = hyphen.movie_quote.get()
        assert quote.quote == "You keep using that word. I do not think it means what you think it means."