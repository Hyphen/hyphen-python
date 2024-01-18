import pytest

@pytest.fixture
def vcr_config():
    return {
        "filter_headers": [("authorization", "xxxx-xxxx-xxxx-xxxx"),
                           ("x-api-key", "xxxx-xxxx-xxxx-xxxx")],
    }

