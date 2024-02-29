from pytest import mark as m
from pytest import raises


from hyphen import HyphenClient


@m.describe("When authenticating a client with Hyphen.ai")
@m.integration
class TestAuth:

    @m.vcr
    @m.context("and valid client settings are provided")
    @m.it("should authenticate successfully")
    def test_m2m_happy_path(self, settings):
        """Test m2m authentication with a valid key set"""
        hyphen = HyphenClient(
            organization_id="xxxxxxxx-xxxxxxx",
            client_id=settings.test_hyphen_client_id,
            client_secret=settings.test_hyphen_client_secret,
            host=settings.test_hyphen_url,
        )

        assert hyphen.authenticated
    @m.vcr
    @m.context("and no or bad auth is provided")
    @m.it("should shortcircuit")
    def test_no_auth_sad_path(self, settings):
        """Test with no or bad auth"""
        with raises(NotImplementedError):  #  in the case of OAuth not implemented
            hyphen = HyphenClient(
                organization_id="xxxx-xxxx-xxxx-xxxx", host=settings.test_hyphen_url
            )

        hyphen = HyphenClient(
            client_id="xxxx-xxxx-xxxx-xxxx",
            client_secret="xxxx-xxxx",
            organization_id="xxxx-xxxx-xxxx-xxxx",
            host=settings.test_hyphen_url,
        )
        assert not hyphen.authenticated
