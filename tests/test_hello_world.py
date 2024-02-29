from pytest import mark as m


from hyphen import HyphenClient


@m.describe("When developing Hyphen")
class TestHelloWorld:

    @m.context(
        "and you just want to make sure your env is set up, paths are working etc."
    )
    @m.it("should return Hello World!")
    def test_hello_world(self):
        """Test the hello world function"""
        assert HyphenClient.helloworld() == "Hello World!"
