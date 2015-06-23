import datetime
import json

import mediaamp
from mediaamp.services import BaseService, Endpoint, services
from mediaamp.exceptions import InvalidTokenError
from mediaamp.utils import decode_datetime, encode_datetime

import mock
import pytest
import requests

url = 'http://example.com'
auth_token = 'XXXXXXXXXX'


@pytest.fixture(scope='module')
def registry():
    with open('service_registry.json') as f:
        return json.load(f)


@pytest.fixture(scope='module')
def session(registry):
    session = mediaamp.Session('fake', 'fake', 'fake')
    session.session = mock.MagicMock()
    session.resolve_domain = mock.Mock(return_value=registry)
    def _sign_in():
        session.auth_token = auth_token
        session.post_sign_in.send(session)
    session.sign_in = mock.Mock(side_effect=_sign_in)
    return session


def test_invalid_token_response(session):
    get = mock.Mock()
    get.status_code = 200
    get.json.return_value = {
        'isException': True,
        'responseCode': 401,
        'description': 'Invalid security token.',
        'title': 'com.theplatform.authentication.api.exception.InvalidTokenException',
    }
    session.session.get.return_value = get
    with pytest.raises(InvalidTokenError):
        session.get('/home')


def test_service_endpoint_initialization(session, registry):

    class TestSvc(BaseService):
        TestEnd = Endpoint(path='fake')

    svc = TestSvc(session, url)
    assert svc.TestEnd.name == 'TestEnd'
    assert svc.TestEnd.urljoin() == url + '/fake/TestEnd'
    assert svc.TestEnd.default_params['account'] == session.account


def test_domain_changes(session):
    assert session.regional_tld == 'com'
    session.region = 'EU3'
    assert session.regional_tld == 'eu'


def test_signin_username(session):
    un = 'foo@bar.com'
    session.username = un
    assert session.signin_username == 'mpx/' + un


def test_post_sign_in_signal(session):

    @session.post_sign_in.connect
    def handle(session):
        assert session.auth_token == auth_token
        handle.signal_handled = True
    handle.signal_handled = False

    assert handle.signal_handled is False
    session.sign_in()
    assert handle.signal_handled is True


def test_service_mappings(session):
    reg = session.registry
    for k, v in services.items():
        assert k in reg


def test_datetimes():
    timestamp = 1435037606000
    dt = decode_datetime(timestamp)
    assert dt.utcoffset() == datetime.timedelta(0)
    assert encode_datetime(dt) == timestamp
