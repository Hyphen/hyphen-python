from pytest import mark as m
from unittest.mock import patch

from hyphen import HyphenClient


@m.describe("When initializing")
@m.unit
class TestNoDuplicateInstances:

    @m.it("should only create one instance")
    def test_one_instance(self, settings):
        with patch("hyphen.client.HTTPRequestClient") as mock_client:
            _ = HyphenClient(
                organization_id="xxxx-xxxx-xxxx-xxxx",
                host=settings.test_hyphen_url,
            )
            mock_client.assert_called_once()
