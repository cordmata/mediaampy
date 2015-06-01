from functools import partial
import re
from .exceptions import ServiceNotAvailable

services = {}

def register(cls):
    if issubclass(cls, BaseService):
        key = getattr(cls, 'registry_key', None)
        if not key:
            key = ' '.join(re.findall('[A-Z][^A-Z]*', cls.__name__))
        services[key] = cls


class Endpoint(object):

    def __init__(self, path=None, name=None, service=None, **kwargs):
        self.path = path
        self.name = name
        self.service = service
        self.default_params = kwargs.copy()
        self.default_params.setdefault('schema', '1.0')

    def urljoin(self, *args):
        parts = (self.service.base_url, self.path, self.name) + args
        return '/'.join([
            part.lstrip('/') for part in parts if part is not None
        ]).rstrip('/')

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
        extra_path = extra_path
        url = self.urljoin(extra_path)
        return self.service.session.request_json(method, url, params=params, **kwargs)

    def __call__(self, **kwargs):
        """ Override default URL parameters.

        Allow custom overrides of defaults to look like object
        initialization.

        """
        self.default_params.update(kwargs)
        return self


class BaseService(object):

    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url
        self.init_endpoints()

    def init_endpoints(self):
        for k, v in self.__class__.__dict__.items():
            if isinstance(v, Endpoint):
                v.service = self
                v(account=self.session.account)
                if v.name is None:
                    v.name = k

    @property
    def Notifications(self):
        return Endpoint(name='notify', service=self, account=self.session.account)


DataEndpoint = partial(Endpoint, path='data')
BusinessEndpoint = partial(Endpoint, path='web')


@register
class AccessDataService(BaseService):
    Permission = DataEndpoint()
    Role = DataEndpoint()
    Authorization = BusinessEndpoint()
    Lookup = BusinessEndpoint()
    Registry = BusinessEndpoint()


@register
class AccountDataService(BaseService):
    Account = DataEndpoint()


@register
class CommerceConfigurationDataService(BaseService):
    CommerceRegistry = DataEndpoint()
    CheckoutConfiguration = DataEndpoint()
    FulfillmentConfiguration = DataEndpoint()
    PaymentConfiguration = DataEndpoint()
    Rule = DataEndpoint()
    RuleSet = DataEndpoint()
    TaxConfiguration = DataEndpoint()

@register
class CommerceEventDataService(BaseService):
    OrderTracking = DataEndpoint()


@register
class CuePointDataService(BaseService):
    CuePoint = Endpoint()
    CuePointType = Endpoint()


@register
class DeliveryDataService(BaseService):
    AccountSettings = DataEndpoint()
    AdPolicy = DataEndpoint()
    Restriction = DataEndpoint()
    UserAgent = DataEndpoint()


@register
class EndUserDataService(BaseService):
    Directory = DataEndpoint()
    Security = DataEndpoint()
    User = DataEndpoint()
    Authentication = BusinessEndpoint()
    Lookup = BusinessEndpoint()
    Self = BusinessEndpoint()


@register
class EntertainmentDataService(BaseService):
    AccountSettings = DataEndpoint()
    Channel = DataEndpoint()
    ChannelSchedule = DataEndpoint()
    Company = DataEndpoint()
    Credit = DataEndpoint()
    Listing = DataEndpoint()
    Location = DataEndpoint()
    Person = DataEndpoint()
    Program = DataEndpoint()
    ProgramAvailability = DataEndpoint()
    Station = DataEndpoint()
    Tag = DataEndpoint()
    TvSeason = DataEndpoint()


@register
class EntertainmentIngestDataService(BaseService):
    IngestConfig = DataEndpoint()
    IngestResult = DataEndpoint()
    Process = BusinessEndpoint()


@register
class EntertainmentFeedsService(BaseService):
    Feed = Endpoint(name='')


@register
class EntitlementDataService(BaseService):
    AccountSettings = DataEndpoint()
    Adapter = DataEndpoint()
    AdapterConfiguration = DataEndpoint()
    Device = DataEndpoint()
    DistributionRight = DataEndpoint()
    DistributionRightLicenseCount = DataEndpoint()
    Entitlement = DataEndpoint()
    LicenseCount = DataEndpoint()
    PhysicalDevice = DataEndpoint()
    ProductDevice = DataEndpoint()
    Rights = DataEndpoint()
    SubjectPolicy = DataEndpoint()
    UserDevice = DataEndpoint()


@register
class EntitlementWebService(BaseService):
    Entitlements = BusinessEndpoint()
    RegisterDevice = BusinessEndpoint()


@register
class EntitlementLicenseService(BaseService):
    ContentAccessRules = BusinessEndpoint(schema='1.2')
    License = BusinessEndpoint(schema='2.5')


@register
class FeedReaderDataService(BaseService):
    registry_key = 'FeedReader Data Service'
    FeedRecord = DataEndpoint()


@register
class FeedsDataService(BaseService):
    FeedAdapter = DataEndpoint()
    FeedConfig = DataEndpoint()


@register
class FeedsService(BaseService):
    Feed = Endpoint(name='')


@register
class FileManagementService(BaseService):
    FileManagement = BusinessEndpoint()


@register
class IngestDataService(BaseService):
    Adapter = DataEndpoint()
    AdapterConfiguration = DataEndpoint()
    Checksum = DataEndpoint()


@register
class IngestService(BaseService):
    ingest = Endpoint()
    test = Endpoint()


@register
class KeyDataService(BaseService):
    Key = DataEndpoint()
    UserKey = DataEndpoint()


@register
class LedgerDataService(BaseService):
    LedgerEntr = DataEndpoint()


@register
class LiveEventDataService(BaseService):
    LiveEncoder = DataEndpoint()
    LiveEvent = DataEndpoint()


@register
class LiveEventService(BaseService):
    Scheduling = BusinessEndpoint()


@register
class MediaDataService(BaseService):
    AccountSettings = DataEndpoint()
    AssetType = DataEndpoint()
    Category = DataEndpoint()
    Media = DataEndpoint()
    MediaDefaults = DataEndpoint()
    MediaFile = DataEndpoint()
    Provider = DataEndpoint()
    Release = DataEndpoint()
    Server = DataEndpoint()


@register
class MessageDataService(BaseService):
    EmailTemplate = DataEndpoint()
    MessageInstruction = DataEndpoint()
    MessageQueue = DataEndpoint()
    NotificationFilter = DataEndpoint()


@register
class PlayerService(BaseService):
    Player = Endpoint(name='p')


@register
class PlayerDataService(BaseService):
    AccountSettings = DataEndpoint()
    ColorScheme = DataEndpoint()
    Layout = DataEndpoint()
    Player = DataEndpoint()
    PlugIn = DataEndpoint()
    Skin = DataEndpoint()


@register
class ProductFeedsService(BaseService):
    Feed = Endpoint(name='')


@register
class ProductDataService(BaseService):
    AccountSettings = DataEndpoint()
    PricingTemplate = DataEndpoint()
    Product = DataEndpoint()
    ProductTag = DataEndpoint()
    Subscription = DataEndpoint()


@register
class PromotionDataService(BaseService):
    Promotion = DataEndpoint()
    PromotionAction = DataEndpoint()
    PromotionCode = DataEndpoint()
    PromotionCondition = DataEndpoint()
    PromotionUseCount = DataEndpoint()


@register
class PublishDataService(BaseService):
    Adapter = DataEndpoint()
    AdapterConfiguration = DataEndpoint()
    PublishProfile = DataEndpoint()


@register
class PublishService(BaseService):
    Publish = BusinessEndpoint()
    Sharing = BusinessEndpoint()


@register
class SelectorService(BaseService):
    Selector = Endpoint(name='')


@register
class SharingDataService(BaseService):
    OutletProfile = DataEndpoint()
    ProviderAdapter = DataEndpoint()


@register
class SocialDataService(BaseService):
    AccountSettings = DataEndpoint()
    Comment = DataEndpoint()
    Rating = DataEndpoint()
    TotalRating = DataEndpoint()


@register
class AdminStorefrontService(BaseService):
    Action = DataEndpoint()
    Contract = DataEndpoint()
    FulfillmentItem = DataEndpoint()
    Order = DataEndpoint()
    OrderFulfillment = DataEndpoint()
    OrderHistory = DataEndpoint()
    OrderItem = DataEndpoint()
    OrderSummary = DataEndpoint()
    PaymentInstrumentInfo = DataEndpoint()
    Shipment = DataEndpoint()
    Checkout = BusinessEndpoint(schema='1.5')
    Payment = BusinessEndpoint(schema='1.1')


@register
class StorefrontService(BaseService):
    Checkout = BusinessEndpoint(schema='1.4')
    Payment = BusinessEndpoint(schema='1.1')
    OrderHistory = DataEndpoint()
    PaymentInstrumentInfo = DataEndpoint()


@register
class TaskService(BaseService):
    Agent = DataEndpoint()
    Batch = DataEndpoint()
    Task = DataEndpoint()
    TaskTemplate = DataEndpoint()
    TaskType = DataEndpoint()


@register
class UserDataService(BaseService):
    Directory = DataEndpoint()
    Security = DataEndpoint()
    User = DataEndpoint()
    Authentication = BusinessEndpoint()
    Lookup = BusinessEndpoint()
    Self = BusinessEndpoint()


@register
class UserProfileDataService(BaseService):
    AccountSettings = DataEndpoint()
    TotalItem = DataEndpoint()
    UserList = DataEndpoint()
    UserListItem = DataEndpoint()
    UserProfile = DataEndpoint()


@register
class ValidationService(BaseService):
    Validation = BusinessEndpoint(schema='1.1')


@register
class ValidationDataService(BaseService):
    ConditionalRule = DataEndpoint()
    ValidationRule = DataEndpoint()
    Validator = DataEndpoint()


@register
class WatchFolderDataService(BaseService):
    registry_key = 'WatchFolder Data Service'
    WatchFolder = DataEndpoint()
    WatchFolderFile = DataEndpoint()


@register
class WorkflowDataService(BaseService):
    ProfileResult = DataEndpoint()
    ProfileStepResult = DataEndpoint()
    WorkflowQueue = DataEndpoint()


