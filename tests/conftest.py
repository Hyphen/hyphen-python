from datetime import datetime
from pathlib import Path
import json
import pytest
from pymongo import MongoClient
import bson

from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    test_hyphen_url: str
    test_hyphen_mongodb_uri: str
    test_hyphen_client_id: str
    test_hyphen_client_secret: str
    test_environment: str = "development"


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
    if settings.test_environment == "CI":
        yield
    else:

        def replace_oids(part):
            if isinstance(part, dict):
                for k, v in part.items():
                    if k in (
                        "_id",
                        "id",
                    ):
                        part[k] = bson.ObjectId(v["oid"])
                    else:
                        part[k] = replace_oids(v)
            return part

        try:
            client = MongoClient(settings.test_hyphen_mongodb_uri)
            db = client.test
            collections = (
                "members",
                "teams",
                "organizations",
            )
            for collection in collections:
                db[collection].delete_many({})
            for collection in collections[::-1]:
                bulk_file = (
                    Path(__file__).parent
                    / f"assets/foundational_test_state/{collection}.json"
                )
                bulk = json.loads(bulk_file.read_text())
                for doc in bulk:
                    doc = replace_oids(doc)
                db[collection].insert_many(bulk)
            yield
        finally:
            if client:
                client.close()


@pytest.fixture(scope="function")
def client_args(settings):
    """returns args for a client logged impersonating TestOrg's Owner"""
    # see /assets/foundational_test_state for these oid values
    return {
        "organization_id": "65dfaa909ea1295731011c5a",
        "impersonate_id": "65dfaa778a70bcfa248c6c03",
        "client_id": settings.test_hyphen_client_id,
        "client_secret": settings.test_hyphen_client_secret,
        "host": settings.test_hyphen_url,
    }
