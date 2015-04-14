from functools import partial
from posixpath import join as urljoin

from . import http
from .exceptions import ServiceNotAvailable

_account_registries = {}  # cache


def for_account(account_id, use_ssl=True):
    """Get the services available to the specified account."""
    if account_id in _account_registries:
        url_map = _account_registries[account_id]
    else:
        url_map = http.resolve_domain_for_account(account_id)
        _account_registries[account_id] = url_map
    if use_ssl:
        return SecureRegistry(url_map)
    else:
        return Registry(url_map)


class Endpoint(object):
    def __init__(self,
                 name,
                 base_url=None,
                 path=None,
                 resource_name=None,
                 **kwargs):
        self.name = name
        self.base_url = base_url
        self.path = path or ''
        self.resource_name = name if resource_name is None else resource_name
        self.default_params = kwargs.copy()
        self.default_params.setdefault('schema', '1.0')

    def __call__(self, **kwargs):
        """ Override default URL parameters.

        Allow custom overrides of defaults to look like object
        initialization.

        """
        self.default_params.update(kwargs)
        return self

    @property
    def url(self):
        return urljoin(
            self.base_url,
            self.path.lstrip('/'),
            self.resource_name.lstrip('/')
        ).rstrip('/')

    def get(self, extra_path=None, **kwargs):
        return self._make_request('get', extra_path, **kwargs)

    def put(self, extra_path=None, **kwargs):
        return self._make_request('put', extra_path, **kwargs)

    def post(self, extra_path=None, **kwargs):
        return self._make_request('post', extra_path, **kwargs)

    def delete(self, extra_path=None, **kwargs):
        return self._make_request('delete', extra_path, **kwargs)

    def _make_request(self, method, extra_path=None, **kwargs):
        # merge default parameters with those supplied
        params = dict(self.default_params, **kwargs.pop('params', {}))
        extra_path = extra_path or ''
        url = urljoin(self.url, extra_path).rstrip('/')
        return http.request_json(method, url, params=params, **kwargs)


class Service(object):

    def __init__(self, url_key, *endpoints, **kwargs):
        self.url_key = url_key
        self.ro_url_key = url_key + ' read-only'
        self.read_only = kwargs.pop('read_only', False)
        self.endpoints = {e.name: e for e in endpoints}

    def __get__(self, registry, type=None):
        """Set the base url on the endpoints when accessed by the registry."""

        if not registry:  # not initialized
            return self

        base_url = None
        if not self.read_only:
            base_url = registry.url_map.get(self.url_key)
        if base_url is None:
            base_url = registry.url_map.get(self.ro_url_key)
        if base_url is None:
            raise ServiceNotAvailable(self)
        for e in self.endpoints.values():
            e.base_url = base_url
        return self

    def __call__(self, read_only=False):
        self.read_only = read_only
        return self

    def __getitem__(self, name):
        return self.endpoints[name]

    def __repr__(self):
        return 'Service({url_key})[{endpoint_names}]'.format(
            url_key=self.url_key,
            endpoint_names=', '.join(self.endpoints.keys())
        )


E = Endpoint
D = partial(Endpoint, path='data')  # DataEndpoint
B = partial(Endpoint, path='web')  # BusinessEndpoint


class Registry(object):

    def __init__(self, url_map):
        self.url_map = url_map

    AccessData = Service(
        'Access Data Service',
        D('Permission'),
        D('Role'),
    )

    AccessManagement = Service(
        'Access Data Service',
        B('Authorization', schema='1.3'),
        B('Lookup'),
        B('Registry'),
    )

    AccountData = Service('Account Data Service', D('Account'))

    CommerceConfigurationData = Service(
        'Commerce Configuration Data Service',
        D('CommerceRegistry'),
        D('CheckoutConfiguration'),
        D('FulfillmentConfiguration'),
        D('PaymentConfiguration'),
        D('Rule'),
        D('RuleSet'),
        D('TaxConfiguration'),
    )

    CommerceEventData = Service(
        'Commerce Event Data Service',
        D('OrderTracking'),
    )

    CuePointData = Service(
        'Cue Point Data Service',
        E('CuePoint'),
        E('CuePointType'),
    )

    DeliveryData = Service(
        'Delivery Data Service',
        D('AccountSettings'),
        D('AdPolicy'),
        D('Restriction'),
        D('UserAgent'),
    )

    EndUserData = Service(
        'End User Data Service',
        D('Directory'),
        D('Security'),
        D('User'),
    )

    EndUser = Service(
        'End User Data Service',
        B('Authentication'),
        B('Lookup'),
        B('Self'),
    )

    EntertainmentData = Service(
        'Entertainment Data Service',
        D('AccountSettings'),
        D('Channel'),
        D('ChannelSchedule'),
        D('Company'),
        D('Credit'),
        D('Listing'),
        D('Location'),
        D('Person'),
        D('Program'),
        D('ProgramAvailability'),
        D('Station'),
        D('Tag'),
        D('TvSeason'),
    )

    EntertainmentIngest = Service(
        'Entertainment Ingest Data Service',
        D('IngestConfig'),
        D('IngestResult'),
        B('Process'),
    )

    EntertainmentFeeds = Service(
        'Entertainment Feeds Service',
        E('Feed', resource_name=''),
    )

    EntitlementData = Service(
        'Entitlement Data Service',
        D('AccountSettings'),
        D('Adapter'),
        D('AdapterConfiguration'),
        D('Device'),
        D('DistributionRight'),
        D('DistributionRightLicenseCount'),
        D('Entitlement'),
        D('LicenseCount'),
        D('PhysicalDevice'),
        D('ProductDevice'),
        D('Rights'),
        D('SubjectPolicy'),
        D('UserDevice'),
    )

    Entitlement = Service(
        'Entitlement Web Service',
        B('Entitlements'),
        B('RegisterDevice'),
    )

    EntitlementLicense = Service(
        'Entitlement License Service',
        B('ContentAccessRules', schema='1.2'),
        B('License', schema='2.5'),
    )

    FeedReaderData = Service(
        'FeedReader Data Service',
        D('FeedRecord'),
    )

    FeedsData = Service(
        'FeedReader Data Service',
        D('FeedAdapter'),
        D('FeedConfig'),
    )

    Feeds = Service(
        'Feeds Service',
        E('Feed', resource_name=''),
    )

    FileManagement = Service(
        'File Management Service',
        B('FileManagement'),
    )

    IngestData = Service(
        'Ingest Data Service',
        D('Adapter'),
        D('AdapterConfiguration'),
        D('Checksum'),
    )

    Ingest = Service('Ingest Service', E('ingest'), E('test'))

    KeyData = Service(
        'Key Data Service',
        D('Key'),
        D('UserKey'),
    )

    LedgerData = Service('Ledger Data Service', D('LedgerEntry'))

    LiveEventData = Service(
        'Live Event Data Service',
        D('LiveEncoder'),
        D('LiveEvent'),
    )

    LiveEvent = Service('Live Event Service',  B('Scheduling'))

    MediaData = Service(
        'Media Data Service',
        D('AccountSettings'),
        D('AssetType'),
        D('Category'),
        D('Media'),
        D('MediaDefaults'),
        D('MediaFile'),
        D('Provider'),
        D('Release'),
        D('Server'),
    )

    MessageData = Service(
        'Message Data Service',
        D('EmailTemplate'),
        D('MessageInstruction'),
        D('MessageQueue'),
        D('NotificationFilter'),
    )

    Player = Service('Player Service', E('Player', resource_name='p'))

    PlayerData = Service(
        'Player Data Service',
        D('AccountSettings'),
        D('ColorScheme'),
        D('Layout'),
        D('Player'),
        D('PlugIn'),
        D('Skin'),
    )

    ProductFeeds = Service(
        'Product Feeds Service',
        E('Feed', resource_name='')
    )

    ProductData = Service(
        'Product Data Service',
        D('AccountSettings'),
        D('PricingTemplate'),
        D('Product'),
        D('ProductTag'),
        D('Subscription'),
    )

    PromotionData = Service(
        'Promotion Data Service',
        D('Promotion'),
        D('PromotionAction'),
        D('PromotionCode'),
        D('PromotionCondition'),
        D('PromotionUseCount'),
    )

    PublishData = Service(
        'Publish Data Service',
        D('Adapter'),
        D('AdapterConfiguration'),
        D('PublishProfile'),
    )

    Publish = Service(
        'Publish Service',
        B('Publish'),
        B('Sharing'),
    )

    Selector = Service('Selector Service', E('Selector', resource_name=''))

    SharingData = Service(
        'Sharing Data Service',
        D('OutletProfile'),
        D('ProviderAdapter'),
    )

    SocialData = Service(
        'Social Data Service',
        D('AccountSettings'),
        D('Comment'),
        D('Rating'),
        D('TotalRating'),
    )

    StorefrontAdmin = Service(
        'Admin Storefront Service',
        D('Action'),
        D('Contract'),
        D('FulfillmentItem'),
        D('Order'),
        D('OrderFulfillment'),
        D('OrderHistory'),
        D('OrderItem'),
        D('OrderSummary'),
        D('PaymentInstrumentInfo'),
        D('Shipment'),
        B('Checkout', schema='1.5'),
        B('Payment', schema='1.1'),
    )

    Storefront = Service(
        'Storefront Service',
        B('Checkout', schema='1.4'),
        B('Payment', schema='1.1'),
        D('OrderHistory'),
        D('PaymentInstrumentInfo'),
    )

    TaskData = Service(
        'Task Service',
        D('Agent'),
        D('Batch'),
        D('Task'),
        D('TaskTemplate'),
        D('TaskType'),
    )

    UserData = Service(
        'User Data Service',
        D('Directory'),
        D('Security'),
        D('User'),
    )

    User = Service(
        'User Data Service',
        B('Authentication'),
        B('Lookup'),
        B('Self'),
    )

    UserProfileData = Service(
        'User Profile Data Service',
        D('AccountSettings'),
        D('TotalItem'),
        D('UserList'),
        D('UserListItem'),
        D('UserProfile'),
    )

    ValidationData = Service(
        'Validation Data Service',
        D('ProfileResult'),
        D('ProfileStepResult'),
        D('WorkflowQueue'),
    )

    Validation = Service('Validation Service', B('Validation', schema='1.1'))

    WatchFolderData = Service(
        'WatchFolder Data Service',
        D('WatchFolder'),
        D('WatchFolderFile'),
    )

    WorkflowData = Service(
        'Validation Data Service',
        D('ConditionalRule'),
        D('ValidationRule'),
        D('Validator'),
    )


class SecureRegistry(Registry):

    def __init__(self, *args, **kwargs):
        super(SecureRegistry, self).__init__(*args, **kwargs)
        self._ensure_https_urls()

    def _ensure_https_urls(self):
        self.url_map = {
            k: v.replace('http://', 'https://')
            for k, v in self.url_map.items()
        }
