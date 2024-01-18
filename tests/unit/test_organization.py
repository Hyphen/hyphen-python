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

    @m.context("and listing organizations")
    @m.it("should list all")
    def test_list_organizations(self, client):
        """Test listing organizations"""
        # TODO: set up in state instead
        for _ in range(5):
            _  = client.organization.create(name=faker.company())

        orgs = client.organization.list()
        assert len(orgs) == 5
        assert len(set([o.id for o in orgs])) == 5