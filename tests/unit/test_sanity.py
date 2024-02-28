from pytest import mark as m


from hyphen.settings import settings
from hyphen import HyphenClient

@m.describe("When working locally")
@m.unit
class TestSanity:

    @m.context("and setting up a dev environment")
    @m.it("should connect to the local  hyphen engine")
    def test_check_dev_setup(self):
        """Test that the dev setup is working"""
        hyphen = HyphenClient(
            host=settings.test_hyphen_url)
        assert hyphen.authenticated
        assert hyphen.healthcheck()