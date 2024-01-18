from pytest import mark as m


from hyphen import HyphenClient
from hyphen.settings import settings

@m.describe("When authenticating a client with Hyphen.ai")
class TestAuth:

    @m.vcr
    @m.context("and using a valid legacy API key")
    @m.it("should authenticate successfully")
    def test_api_key_happy_path(self):
        """Test m2m authentication with a valid legacy API key"""
        hyphen = HyphenClient(
            legacy_api_key=settings.legacy_api_key,
            host=settings.development_hyphen_uri)

        assert hyphen.authenticated

    @m.context("and no auth is provided")
    @m.it("should shortcircuit")
    def test_no_auth_sad_path(self):
        """Test without any auth"""

        hyphen = HyphenClient(
            host=settings.development_hyphen_uri)

        assert hyphen.authenticated