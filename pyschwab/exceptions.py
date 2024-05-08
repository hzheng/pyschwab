class BrokerAPIException(Exception):
    """Base exception class for Broker API issues."""
    def __init__(self, message="An error occurred with the Broker API"):
        self.message = message
        super().__init__(self.message)


class HTTPErrorException(BrokerAPIException):
    """Exception raised for HTTP errors (400-599)."""
    def __init__(self, message="HTTP error occurred"):
        super().__init__(message)


class BadRequestException(BrokerAPIException):
    """Exception raised for HTTP client errors (400-499)."""
    def __init__(self, message="Client error occurred"):
        super().__init__(message)


class ServerErrorException(BrokerAPIException):
    """Exception raised for HTTP server errors (500-599)."""
    def __init__(self, message="Server error occurred"):
        super().__init__(message)


class InternetConnectionException(BrokerAPIException):
    """Exception raised for internet connectivity issues."""
    def __init__(self, message="Failed to connect to the internet"):
        super().__init__(message)
