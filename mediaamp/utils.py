from datetime import datetime
from calendar import timegm
from pytz import UTC


def decode_datetime(dt_in_millis):
    return datetime.fromtimestamp(dt_in_millis / 1000, UTC)


def encode_datetime(dt):
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        # if naive assume UTC as that is what the API expects
        dt = UTC.localize(dt)
    return timegm(dt.astimezone(UTC).timetuple()) * 1000
