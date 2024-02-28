from pytest import mark as m


from hyphen.settings import settings
from hyphen import HyphenClient

@m.describe("When working locally")
@m.unit
class TestSanity:

    @m.context("and setting up a dev environment")
    @m.it("should connect to the local hyphen engine")
    def test_check_dev_setup(self, settings):
        """Test that the dev setup is working"""
        hyphen = HyphenClient(
            host=settings.test_hyphen_url,
            client_id=settings.test_hyphen_client_id,
            client_secret=settings.test_hyphen_client_secret,
            organization_id="xxxx-xxxx-xxxx"
        )
        assert hyphen.authenticated
        assert hyphen.healthcheck()