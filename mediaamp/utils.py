from datetime import datetime
from time import mktime


def normalize_registry_name(name):
    name.lower().replace(' ', '_')


def decode_datetime(dt_in_millis):
    return datetime.utcfromtimestamp(dt_in_millis / 1000)


def encode_datetime(dt):
    return int(mktime(dt.utctimetuple()) * 1000)