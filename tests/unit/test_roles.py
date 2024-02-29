from pytest import mark as m
from hyphen.roles import Role


@m.describe("Roles")
class TestRole:

    @m.it("should be equal to a string with the same value")
    def test_role_equals_string(self):
        role = Role(name="teamOwner", context="team", context_id="123")
        assert role == "teamOwner"
        assert not role == "teamMember"
