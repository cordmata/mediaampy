import mediaamp
from mediaamp import http
from mediaamp.services import Service, Endpoint, Registry
from mediaamp.exceptions import AuthenticationError, ServiceNotAvailable

import mock
import pytest
import requests

url = 'http://example.com'


def test_service():
    s = Service(url, Endpoint('Test'))
    assert isinstance(s['Test'], Endpoint)
    assert s.Test.resource_name == 'Test'
    assert s.Test.base_url == url


def test_endpoint():
    path = 'web'
    name = 'Account'
    e = Endpoint(name, url, path, form='cjson')
    assert e.default_params == dict(schema='1.0', form='cjson')
    assert e.url == url + '/web/Account'
    e(new_param='hi')
    assert 'new_param' in e.default_params
    e = Endpoint(name, url, path, resource_name='')
    assert e.url == url + '/web'


def test_registry():
    url_map = {
        'Account Data Service': url,
        'Cue Point Data Service': url,
    }
    r = Registry(url_map)
    account = r.Account_Data_Service
    assert isinstance(account, Service)
    endpoint = account.Account
    assert isinstance(endpoint, Endpoint)
    assert endpoint.base_url == url
    assert endpoint.url == url + '/data/Account'
    with pytest.raises(AttributeError):
        r.access_data_service.Permission
    cps = r['Cue Point Data Service'].CuePoint
    assert cps.url == url + '/CuePoint'
    assert isinstance(r['Account Data Service'].Notifications, Endpoint)


def test_domain_changes():
    assert http.regional_tld() == 'com'
    mediaamp.region = 'EU3'
    assert http.regional_tld() == 'eu'


def test_signin_username():
    mediaamp.username = None
    with pytest.raises(AuthenticationError):  # when module not configured
        http.signin_username()
    un = 'foo@bar.com'
    mediaamp.username = un
    assert http.signin_username() == 'mpx/' + un


@pytest.fixture(scope='module')
def invalid_token_response():
    resp = mock.Mock(spec=requests.models.Response)
    resp.json.return_value = {
        'isException': True,
        'responseCode': 401,
        'description': 'Invalid security token.',
        'title': 'com.theplatform.authentication.api.exception.InvalidTokenException',
    }
    resp.status_code = 200
    return resp

# TODO: Test http with mocks/responses
