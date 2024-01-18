from pytest import mark as m
from pytest import fixture
from faker import Faker

from hyphen.settings import settings
from hyphen import HyphenClient

faker = Faker()

@m.describe("When working with organizations")
class TestOrganization:

    @fixture(scope="function")
    def client(self):
        """Return a HyphenClient instance"""
        hyphen = HyphenClient(
            legacy_api_key=settings.local_api_key,
            host=settings.local_hyphen_uri)
        return hyphen

    @m.context("and creating a new organization")
    @m.it("should create successfully")
    def test_create_organization(self, client):
        """Test creating a new organization"""
        name = faker.company()
        org  = client.organization.create(name=name)
        assert org.id

    @m.context("and reading an organization")
    @m.it("should read successfully")
    def test_read_organization(self, client):
        """Test reading an organization"""
        # TODO: set up in state instead
        name = faker.company()
        org  = client.organization.create(name=name)
        assert org.id
        org2 = client.organization.read(org.id)
        assert org2.id == org.id
        assert org2.name == org.name