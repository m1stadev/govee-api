from datetime import datetime


class GoveeError(Exception):
    pass


class APIError(GoveeError):
    pass


class AuthError(APIError):
    pass


class DevicesError(APIError):
    pass


class RatelimitError(APIError):
    def __init__(self, msg: str, time: int):
        self.message = msg
        self.time = datetime.fromtimestamp(time)

    def __str__(self): return self.message
