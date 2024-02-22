from pytest import mark as m
from httpx import URL
import hyphen

class TestDebugProfile:

    @m.vcr()
    def test_debug_profile(self):
        client = hyphen.HyphenClient(
            host="http://engine:3000",
            organization_id='65d76d14d620e4b4a4d06e6e')
        unauthed = client.debug_profile
        assert unauthed == {'http_client': {'client_type': 'HTTPRequestClient', 'auth_token_expires': 0.0, 'm2m_credentials': ['chat', 'OE8e[redacted]Zo4j'], 'headers': {'accept-encoding': 'gzip, deflate', 'connection': 'keep-alive', 'user-agent': 'python-httpx/0.26.0', 'content-type': 'application/json', 'accept': 'application/json'}, 'authorization_header': None}, 'host': 'http://engine:3000', 'organization_id': '65d76d14d620e4b4a4d06e6e', 'on_behalf_of': None}
        _ = client.organizations.list()
        authed = client.debug_profile
        assert authed == {'http_client': {'client_type': 'HTTPRequestClient', 'auth_token_expires': 1708623548.138, 'm2m_credentials': ['chat', 'OE8e[redacted]Zo4j'], 'headers': {'accept-encoding': 'gzip, deflate', 'connection': 'keep-alive', 'user-agent': 'python-httpx/0.26.0', 'content-type': 'application/json', 'accept': 'application/json'}, 'authorization_header': 'Bearer e[redacted]sy1A'}, 'host': 'http://engine:3000', 'organization_id': '65d76d14d620e4b4a4d06e6e', 'on_behalf_of': None}
