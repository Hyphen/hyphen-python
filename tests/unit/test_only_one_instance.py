from pytest import mark as m
from unittest.mock import patch

from hyphen.settings import settings
from hyphen import HyphenClient

@m.describe("When initializing")
@m.unit
class TestNoDuplicateInstances:

    @m.it("should only create one instance")
    def test_one_instance(self):
        with patch("hyphen.client.HTTPRequestClient") as mock_client:
            hyphen = HyphenClient(
                legacy_api_key=settings.local_api_key,
                host=settings.local_hyphen_uri)
            mock_client.assert_called_once()
