import mediaamp as ma

from .exceptions import (
    InvalidTokenError,
    AuthenticationError,
    MediaAmpError,
    wrap_http_error,
    raise_for_json_exception,
)

import requests
from requests.auth import HTTPBasicAuth

session = requests.Session()
session.headers.update({
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'Python Mediaamp %s' % ma.__version__,
})


def request_json(method,
                 url,
                 retry_sign_in=True,
                 is_signin_request=False,
                 **kwargs):
    """ Requests JSON content from the supplied URL.

    This is the primary function to be used to make requests to the MPX API.
    Not only does it ensure that the body of the response can be encoded as
    Python via JSON, it also wraps exceptions and will auto-login using
    the supplied credentials when necessary (e.g. when a token expires).

    This API is known to return 200 statuses for requests that fail. It's
    their convention to include the HTTP response code in the body of
    the JSON returned. This checks for that case and turns them into actual
    exceptions.

    """
    if ma.current_token is not None:
        session.auth = HTTPBasicAuth('', ma.current_token)
    elif not is_signin_request:
        sign_in(ma.token_duration, ma.token_idle_timeout)
    response = getattr(session, method)(url, **kwargs)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        wrap_http_error(e)

    try:
        data = response.json()
    except ValueError:
        raise MediaAmpError('Response body can not be read as JSON. ')

    try:
        raise_for_json_exception(data)
    except InvalidTokenError:
        if retry_sign_in:
            sign_in(ma.token_duration, ma.token_idle_timeout)
            return request_json(method, url, retry_sign_in=False, **kwargs)
        else:
            raise

    return data


def get(url, **kwargs):
    return request_json('get', url, **kwargs)


def put(url, **kwargs):
    return request_json('put', url, **kwargs)


def post(url, **kwargs):
    return request_json('post', url, **kwargs)


def delete(url, **kwargs):
    return request_json('delete', url, **kwargs)


##############################################################################
#
# Implementations of endpoint calls needed to obtain a service registry.
#
##############################################################################
SIGN_IN_URL = 'https://identity.auth.theplatform.{tld}/idm/web/Authentication/signIn'
REGISTRY_URL = 'https://access.auth.theplatform.{tld}/web/Registry/resolveDomain'


def resolve_domain_for_account(account_id):
    url = REGISTRY_URL.format(tld=regional_tld())
    resp = get(url, params={
        'schema': '1.1',
        '_accountId': account_id,
    })
    try:
        return resp['resolveDomainResponse']
    except KeyError:
        raise MediaAmpError('Unexpected response loading registry.')


def sign_in(duration=43200000, idle_timeout=14400000):
    ma.current_token = None
    session.auth = HTTPBasicAuth(signin_username(), ma.password)
    result = get(
        SIGN_IN_URL.format(tld=regional_tld()),
        is_signin_request=True,
        params={
            'schema': '1.0',
            '_duration': duration,
            '_idleTimeout': idle_timeout,
        }
    )
    try:
        ma.current_token = result['signInResponse']['token']
    except KeyError:
        raise AuthenticationError('Could not retrieve token.')


def signin_username():
    if not ma.user_directory or not ma.username:
        raise AuthenticationError(
            'Package not configured. Please set `mediaamp.username` and '
            '`mediaamp.password` before using the library. If your account '
            'region is not US1 please set `mediaamp.user_directory` as well.')
    return ma.user_directory + '/' + ma.username


def regional_tld():
    return 'eu' if 'eu' in ma.region.lower() else 'com'
