from pytest import mark as m


from hyphen import HyphenClient
from hyphen.settings import settings

@m.describe("When authenticating a client with Hyphen.ai")
class TestAuth:

    @m.context("and using a valid legacy API key")
    @m.it("should authenticate successfully")
    def test_api_key_happy_path(self):
        """Test m2m authentication with a valid legacy API key"""
        hyphen = HyphenClient(
            api_key=settings.legacy_api_key,
            host=settings.development_hyphen_uri)

        assert hyphen.healthcheck()
        assert hyphen.authenticated
