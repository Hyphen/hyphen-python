from typing import Generator
from pytest import mark as m
from pytest import fixture
from faker import Faker

from hyphen import HyphenClient

faker = Faker()


@m.describe("When working with organizations")
@m.unit
class TestOrganization:

    @fixture(scope="function")
    def client(self, settings):
        """Return a HyphenClient instance"""
        hyphen = HyphenClient(
            organization_id="xxxx-xxxx-xxxx",
            host=settings.test_hyphen_url,
            client_id=settings.test_hyphen_client_id,
            client_secret=settings.test_hyphen_client_secret,
        )
        return hyphen

    @m.context("and creating a new organization")
    @m.it("should create successfully")
    @m.vcr()
    def test_create_organization(self, client):
        """Test creating a new organization"""
        name = faker.company()
        org = client.organization.create(name=name)
        assert org.id

    @m.context("and reading an organization")
    @m.it("should read successfully")
    @m.vcr()
    def test_read_organization(self, client):
        """Test reading an organization"""
        # TODO: set up in state instead
        name = faker.company()
        org = client.organization.create(name=name)
        assert org.id
        org2 = client.organization.read(org.id)
        assert org2.id == org.id
        assert org2.name == org.name

    @m.context("and listing organizations")
    @m.it("should list all")
    @m.vcr()
    def test_list_organizations(self, client):
        """Test listing organizations"""
        # TODO: set up in state instead, right now all this janky math is due to the remote db

        ids = set()

        def cycle_results(ids):
            for org in client.organization.list():
                ids.add(org.id)

        cycle_results(ids)
        first_count = len(ids)

        for _ in range(5):
            _ = client.organization.create(name=faker.company())

        cycle_results(ids)
        second_count = len(ids)

        assert (second_count - first_count) == 5
