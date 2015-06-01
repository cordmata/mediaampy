from blinker import Signal
import requests
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.poolmanager import PoolManager
import ssl

from . import __version__, __title__
from .services import services
from .exceptions import (
    InvalidTokenError,
    AuthenticationError,
    MediaAmpError,
    wrap_http_error,
    raise_for_json_exception,
)


SIGN_IN_URL = 'https://identity.auth.theplatform.{tld}/idm/web/Authentication/signIn'
REGISTRY_URL = 'https://access.auth.theplatform.{tld}/web/Registry/resolveDomain'


class Session(object):

    def __init__(self,
                 username,
                 password,
                 account_id,
                 auth_token=None,
                 user_directory='mpx',
                 region='US1',
                 service_registry=None,
                 token_duration=43200000,       # 12 hours
                 token_idle_timeout=14400000,   # 4 hours
                 use_ssl=True,
                 ):

        self.username = username
        self.password = password
        self.account = account_id
        self.auth_token = auth_token
        self.user_directory = user_directory
        self.region = region
        self.token_duration = token_duration
        self.token_idle_timeout = token_idle_timeout
        self.use_ssl = use_ssl
        self.registry_url = REGISTRY_URL.format(tld=self.regional_tld)
        self.signin_url = SIGN_IN_URL.format(tld=self.regional_tld)
        self.post_sign_in = Signal()
        self._registry = service_registry
        self.session = requests.Session()
        self.session.mount('https://', TLS1Adapter())
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Python Mediaamp %s' % __version__,
        })

    @property
    def registry(self):
        if self._registry is None:
            self._registry = self.resolve_domain()
        return self._registry

    @property
    def regional_tld(self):
        return 'eu' if 'eu' in self.region.lower() else 'com'

    @property
    def signin_username(self):
        return self.user_directory + '/' + self.username

    def resolve_domain(self):
        resp = self.get(self.registry_url, params={
            'schema': '1.1',
            '_accountId': self.account,
        })
        try:
            return resp['resolveDomainResponse']
        except KeyError:
            raise MediaAmpError('Unexpected response loading registry.')

    def sign_in(self):
        self.auth_token = None
        self.session.auth = HTTPBasicAuth(self.signin_username, self.password)
        result = self.get(self.signin_url, is_signin_request=True, params={
            'schema': '1.0',
            '_duration': self.token_duration,
            '_idleTimeout': self.token_idle_timeout,
        })
        try:
            self.auth_token = result['signInResponse']['token']
        except KeyError:
            raise AuthenticationError('Could not retrieve token.')
        self.post_sign_in.send(self)

    def request_json(self, method, url, retry_sign_in=True, is_signin_request=False, **kwargs):
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
        if self.auth_token is not None:
            self.session.auth = HTTPBasicAuth('', self.auth_token)
        elif not is_signin_request:
            self.sign_in()

        response = getattr(self.session, method)(url, **kwargs)

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
                self.sign_in()
                return self.request_json(method, url, retry_sign_in=False, **kwargs)
            else:
                raise

        return data

    def get(self, url, **kwargs):
        return self.request_json('get', url, **kwargs)

    def put(self, url, **kwargs):
        return self.request_json('put', url, **kwargs)

    def post(self, url, **kwargs):
        return self.request_json('post', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request_json('delete', url, **kwargs)

    def __getitem__(self, key):
        url = self.registry.get(key)
        if url is None:
            url = self.registry(key + ' read-only')
        if url is None:
            raise KeyError(key + ' not available.')
        if self.use_ssl:
            url = url.replace('http://', 'https://')
        return services[key](self, url)


class TLS1Adapter(HTTPAdapter):
    """ Force requests SSL to use TLS 1.

    As of 4/30/2015 thePlatform APIs use TLS 1.2 which causes EOF
    errors with the default adapter. They are planning to update to
    SHA-256 certs @ June 15. see:

    https://help.theplatform.com/display/trc/2015+certificate+security+upgrade

    """

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLSv1
        )
