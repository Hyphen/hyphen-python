from hyphen import HyphenClient

class TestHelloWorld:
    def test_hello_world(self):
        hyphen = HyphenClient()
        assert hyphen.helloworld() == "Hello World!"