from collections import defaultdict


class MediaAmpError(Exception):
    """Unspecified error occurred."""


class ClientError(MediaAmpError):
    """Bad request or unauthorized request."""


class NotFound(MediaAmpError):
    """Requested resource not found."""


class ServerError(MediaAmpError):
    """Remote server error."""


class AuthenticationError(MediaAmpError):
    """Unable to authenticate with supplied credentials."""


class InvalidTokenError(AuthenticationError):
    """Supplied authentication token is not valid or has expired."""


class ServiceNotAvailable(MediaAmpError):
    """Could not find service by name in the registry."""


def wrap_http_error(error):
    response = error.response
    error_class = http_status_map[response.status_code]
    raise error_class(response.text)


http_status_map = defaultdict(lambda: MediaAmpError)
for code in range(400, 500):
    http_status_map[code] = ClientError
for code in (401, 403):
    http_status_map[code] = AuthenticationError
http_status_map[404] = NotFound
for code in range(500, 600):
    http_status_map[code] = ServerError


def raise_for_json_exception(data):
    if isinstance(data, dict) and data.get('isException'):
        status_code = data.get('responseCode', 400)
        description = data.get('description', 'Bad Request')
        title = data.get('title')
        if title in json_error_title_map:
            exc = json_error_title_map[title]
        elif 'invalid security token' in description.lower():
            exc = InvalidTokenError
        else:
            exc = http_status_map[status_code]
        raise exc(description)


json_error_title_map = {
    'com.theplatform.authentication.api.exception.InvalidTokenException': InvalidTokenError,
    'ObjectNotFoundException': NotFound,
}
