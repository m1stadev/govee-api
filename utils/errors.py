class GoveeError(Exception):
    pass

class APIError(GoveeError):
    pass


class AuthError(APIError):
    pass


class RatelimitError(APIError):
    pass
