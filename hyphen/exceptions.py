class HyphenException(Exception):
    """base exception for all Hyphen exceptions"""


class HyphenApiException(HyphenException):
    """Raised when the Hyphen.ai API returns an error"""


class AmbiguousOrganizationException(HyphenException):
    """Raised when the client is unable to determine the organization associated with the provided credentials."""


class IncorrectMethodException(HyphenException):
    """Raised when admittedly confusing method calls are confused."""


class AuthenticationException(HyphenException):
    """Raised when a request is made without authentication, or when authentication fails"""

    def __init__(self, code: int):
        self.message = "Authentication failed or required"
        self.code = code

    def __str__(self):
        if self.code == 401:
            return f"Authentication failed: {self.message}"
        if self.code == 403:
            return f"Authentication required: {self.message}"
        return f"Authentication failed or required: {self.message}"
