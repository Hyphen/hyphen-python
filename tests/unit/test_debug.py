from pytest import mark as m
from httpx import URL
import hyphen


class TestDebugProfile:

    @m.vcr()
    def test_debug_profile(self, settings):
        client = hyphen.HyphenClient(
            host=settings.test_hyphen_url,
            organization_id="65df56ba846e0004123c6879",  # see /assets/foundational_test_state
            client_id=settings.test_hyphen_client_id,
            client_secret=settings.test_hyphen_client_secret,
        )

        unauthed = client.debug_profile
        guts = unauthed["http_client"]
        assert guts["client_type"] == "HTTPRequestClient"
        assert guts["auth_token_expires"] == 0.0
        assert "[redacted]" in guts["m2m_credentials"][1]
        assert guts["authorization_header"] is None
        # assert guts["on_behalf_of"] is None
        _ = client.organizations.list()
        authed = client.debug_profile
        guts = authed["http_client"]
        assert guts["client_type"] == "HTTPRequestClient"
        assert guts["auth_token_expires"] > 0.0
        assert "[redacted]" in guts["m2m_credentials"][1]
        assert "Bearer" in guts["authorization_header"]
        # assert guts["on_behalf_of"] is None
        # assert guts["organization_id"] is not None
