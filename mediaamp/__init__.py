__version__ = '0.1.1'

from . import services, http, exceptions  # noqa


# configuration variables
username = None
password = None
user_directory = 'mpx'
region = 'US1'
token_duration = 43200000       # 12 hours
token_idle_timeout = 14400000   # 4 hours

current_token = None
