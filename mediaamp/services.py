from functools import partial
from posixpath import join as urljoin

from . import http

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

    def __init__(self, base_url, *endpoints, **kwargs):
        self.base_url = base_url
        self.endpoints = {e.name: e for e in endpoints}
        for e in self.endpoints.values():
            e.base_url = self.base_url

    @property
    def Notifications(self):
        return Endpoint('notify', self.base_url)

    def __getitem__(self, name):
        return self.endpoints[name]

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError('Endpoint not found.')

    def __repr__(self):
        return 'Service()[{endpoint_names}]'.format(
            endpoint_names=', '.join(self.endpoints.keys())
        )


class Registry(object):
    _services = {}

    @classmethod
    def register(cls, service_name, *endpoints):
        cls._services[cls.normalize_name(service_name)] = endpoints

    @staticmethod
    def normalize_name(name):
        return name.lower().replace(' ', '_')

    def __init__(self, url_map):
        self.url_map = {
            self.normalize_name(k): v
            for k, v in url_map.items()
        }

    def __getitem__(self, name):
        name = self.normalize_name(name)
        endpoints = self._services[name]
        url = self.url_map.get(name)
        if url is None:
            url = self.url_map.get(name + ' read-only')
        if url is None:
            raise KeyError('Service not found')
        return Service(url, *endpoints)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError('Service not found')


class SecureRegistry(Registry):

    def __init__(self, *args, **kwargs):
        super(SecureRegistry, self).__init__(*args, **kwargs)
        self._ensure_https_urls()

    def _ensure_https_urls(self):
        self.url_map = {
            k: v.replace('http://', 'https://')
            for k, v in self.url_map.items()
        }


E = Endpoint
D = partial(Endpoint, path='data')  # DataEndpoint
B = partial(Endpoint, path='web')   # BusinessEndpoint


Registry.register(
    'Access Data Service',
    D('Permission'),
    D('Role'),
    B('Authorization', schema='1.3'),
    B('Lookup'),
    B('Registry'),
)


Registry.register(
    'Account Data Service',
    D('Account')
)

Registry.register(
    'Commerce Configuration Data Service',
    D('CommerceRegistry'),
    D('CheckoutConfiguration'),
    D('FulfillmentConfiguration'),
    D('PaymentConfiguration'),
    D('Rule'),
    D('RuleSet'),
    D('TaxConfiguration'),
)

Registry.register(
    'Commerce Event Data Service',
    D('OrderTracking'),
)

Registry.register(
    'Cue Point Data Service',
    E('CuePoint'),
    E('CuePointType'),
)

Registry.register(
    'Delivery Data Service',
    D('AccountSettings'),
    D('AdPolicy'),
    D('Restriction'),
    D('UserAgent'),
)

Registry.register(
    'End User Data Service',
    D('Directory'),
    D('Security'),
    D('User'),
    B('Authentication'),
    B('Lookup'),
    B('Self'),
)

Registry.register(
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

Registry.register(
    'Entertainment Ingest Data Service',
    D('IngestConfig'),
    D('IngestResult'),
    B('Process'),
)

Registry.register(
    'Entertainment Feeds Service',
    E('Feed', resource_name=''),
)

Registry.register(
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

Registry.register(
    'Entitlement Web Service',
    B('Entitlements'),
    B('RegisterDevice'),
)

Registry.register(
    'Entitlement License Service',
    B('ContentAccessRules', schema='1.2'),
    B('License', schema='2.5'),
)

Registry.register(
    'FeedReader Data Service',
    D('FeedRecord'),
)

Registry.register(
    'FeedReader Data Service',
    D('FeedAdapter'),
    D('FeedConfig'),
)

Registry.register(
    'Feeds Service',
    E('Feed', resource_name=''),
)

Registry.register(
    'File Management Service',
    B('FileManagement'),
)

Registry.register(
    'Ingest Data Service',
    D('Adapter'),
    D('AdapterConfiguration'),
    D('Checksum'),
)

Registry.register(
    'Ingest Service',
    E('ingest'),
    E('test')
)

Registry.register(
    'Key Data Service',
    D('Key'),
    D('UserKey'),
)

Registry.register(
    'Ledger Data Service',
    D('LedgerEntry')
)

Registry.register(
    'Live Event Data Service',
    D('LiveEncoder'),
    D('LiveEvent'),
)

Registry.register(
    'Live Event Service',
    B('Scheduling'),
)

Registry.register(
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

Registry.register(
    'Message Data Service',
    D('EmailTemplate'),
    D('MessageInstruction'),
    D('MessageQueue'),
    D('NotificationFilter'),
)

Registry.register(
    'Player Service',
    E('Player', resource_name='p'),
)

Registry.register(
    'Player Data Service',
    D('AccountSettings'),
    D('ColorScheme'),
    D('Layout'),
    D('Player'),
    D('PlugIn'),
    D('Skin'),
)

Registry.register(
    'Product Feeds Service',
    E('Feed', resource_name='')
)

Registry.register(
    'Product Data Service',
    D('AccountSettings'),
    D('PricingTemplate'),
    D('Product'),
    D('ProductTag'),
    D('Subscription'),
)

Registry.register(
    'Promotion Data Service',
    D('Promotion'),
    D('PromotionAction'),
    D('PromotionCode'),
    D('PromotionCondition'),
    D('PromotionUseCount'),
)

Registry.register(
    'Publish Data Service',
    D('Adapter'),
    D('AdapterConfiguration'),
    D('PublishProfile'),
)

Registry.register(
    'Publish Service',
    B('Publish'),
    B('Sharing'),
)

Registry.register('Selector Service', E('Selector', resource_name=''))

Registry.register(
    'Sharing Data Service',
    D('OutletProfile'),
    D('ProviderAdapter'),
)

Registry.register(
    'Social Data Service',
    D('AccountSettings'),
    D('Comment'),
    D('Rating'),
    D('TotalRating'),
)

Registry.register(
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

Registry.register(
    'Storefront Service',
    B('Checkout', schema='1.4'),
    B('Payment', schema='1.1'),
    D('OrderHistory'),
    D('PaymentInstrumentInfo'),
)

Registry.register(
    'Task Service',
    D('Agent'),
    D('Batch'),
    D('Task'),
    D('TaskTemplate'),
    D('TaskType'),
)

Registry.register(
    'User Data Service',
    D('Directory'),
    D('Security'),
    D('User'),
)

Registry.register(
    'User Data Service',
    B('Authentication'),
    B('Lookup'),
    B('Self'),
)

Registry.register(
    'User Profile Data Service',
    D('AccountSettings'),
    D('TotalItem'),
    D('UserList'),
    D('UserListItem'),
    D('UserProfile'),
)

Registry.register(
    'Validation Data Service',
    D('ProfileResult'),
    D('ProfileStepResult'),
    D('WorkflowQueue'),
)

Registry.register(
    'Validation Service',
    B('Validation', schema='1.1')
)

Registry.register(
    'WatchFolder Data Service',
    D('WatchFolder'),
    D('WatchFolderFile'),
)

Registry.register(
    'Validation Data Service',
    D('ConditionalRule'),
    D('ValidationRule'),
    D('Validator'),
)
