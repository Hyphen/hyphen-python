import subprocess
import pytest

from hyphen.settings import settings

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
    if "TODO: how do we reset this remotely on each test?":
        return
    reset_string = f'mongosh "mongodb://{settings.local_hyphen_db_username}:{settings.local_hyphen_db_password}@{settings.local_hyphen_uri}:27017" --authenticationDatabase admin --eval "db.dropDatabase()"'
    subprocess.run(reset_string)
