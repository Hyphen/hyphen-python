from pytest import mark as m
from pytest import raises


from hyphen import HyphenClient
from hyphen.settings import settings

@m.describe("When authenticating a client with Hyphen.ai")
@m.integration
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

    @m.context("and no or bad auth is provided")
    @m.it("should shortcircuit")
    def test_no_auth_sad_path(self):
        """Test with no or bad auth"""
        with raises(AssertionError):
            hyphen = HyphenClient(
                host=settings.development_hyphen_uri)

        hyphen = HyphenClient(
            legacy_api_key="xxxx-xxxx-xxxx-xxxx",
            host=settings.development_hyphen_uri)
        assert not hyphen.authenticated