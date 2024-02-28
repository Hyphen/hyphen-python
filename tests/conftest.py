from pathlib import Path
import json
import pytest
from pymongo import MongoClient

from pydantic_settings import BaseSettings

from hyphen.settings import settings

class TestSettings(BaseSettings):
    test_hyphen_url: str
    test_hyphen_mongodb_uri: str

test_settings = TestSettings()

@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("authorization", "xxxx-xxxx-xxxx-xxxx"),
                           ("x-api-key", "xxxx-xxxx-xxxx-xxxx"),
                           ("Report-To", "xxxx-xxxx-xxxx-xxxx"),
                           ("Server", "xxxx-xxxx-xxxx-xxxx")],
    }

@pytest.fixture(scope="function", autouse=True)
def reset_engine_db():
    client = MongoClient(test_settings.test_hyphen_mongodb_uri)
    db = client.test
    for collection in ("members", "teams", "organizations"):
        db[collection].delete_many({})
        bulk_file = Path(__file__).parent / f"assets/foundational_test_state/{collection}.json"
        bulk = json.loads(bulk_file.read_text())
        db[collection].insert_many(bulk)