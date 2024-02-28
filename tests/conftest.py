from datetime import datetime
from pathlib import Path
import json
import pytest
from pymongo import MongoClient

from pydantic_settings import BaseSettings

class TestSettings(BaseSettings):
    test_hyphen_url: str
    test_hyphen_mongodb_uri: str
    test_hyphen_client_id: str
    test_hyphen_client_secret: str


@pytest.fixture(scope="module")
def settings():
    return TestSettings()

def scrub_m2m_request(request):
    if request.url.endswith("/api/auth/m2m"):
        request.body = b'{"clientId":"secret","clientSecret":"secret"}'
    return request


def scrub_m2m_response(response):
    try:
        if response["body"]["string"].startswith(b'{"access_token":"'):
            response["body"]["string"] = (
                '{"access_token":"secret", '
                '"access_token_expires_in":3600000,'
                '"id_token":"secret",'
                f'"access_token_expires_at":{(datetime.now().timestamp() + 3600) * 1000},'
                '"token_type":"Bearer"}'
            ).encode("utf-8")
    except KeyError:
        pass
    return response

@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("authorization", "xxxxx-xxxxx-xxxxx")],
        "before_record_request": scrub_m2m_request,
        "before_record_response": scrub_m2m_response,
    }

@pytest.fixture(scope="function", autouse=True)
def reset_engine_db(settings):
    client = None
    try:
        client = MongoClient(settings.test_hyphen_mongodb_uri)
        db = client.test
        for collection in ("members", "teams", "organizations"):
            db[collection].delete_many({})
            bulk_file = Path(__file__).parent / f"assets/foundational_test_state/{collection}.json"
            bulk = json.loads(bulk_file.read_text())
            db[collection].insert_many(bulk)
        yield
    finally:
        if client:
            client.close()