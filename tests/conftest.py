import pytest

@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("authorization", "xxxx-xxxx-xxxx-xxxx"),
                           ("x-api-key", "xxxx-xxxx-xxxx-xxxx"),
                           ("Report-To", "xxxx-xxxx-xxxx-xxxx"),
                           ("Server", "xxxx-xxxx-xxxx-xxxx")],
    }

