from datetime import datetime
import time
import dateutil


def current_time_millis() -> int:
    '''
    Gives the current millisecond precision unix timestamp, as an int
    :return: millisecond unix timestamp
    '''
    return int(round(time.time() * 1000))


def iso_to_millis(rfc3339_timestamp: str) -> int:
    """
    Converts an rfc3339 formatted timestamp, of any precision, to a millisecond resolution unix timestamp
    Can accept the +00:00 timezone format, or Z
    :param rfc3339_timestamp: rfc3339 (or maybe iso8601) formatted timestamp.
    examples: 2024-04-01T16:08:10+0000
              2024-04-01T16:08:10-0400
              2024-04-01T16:08:10-04:00
              2024-04-01T16:08:10Z
              2024-04-01T16:08:10      # Will assume UTC
    :return: millisecond unix timestamp
    """

    dt = dateutil.parser.parse(rfc3339_timestamp)

    # If there is no time zone info, force it to UTC without changing the clock time
    # Without this, it assumes it's _local_ time, not UTC!
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=dateutil.tz.tzutc())

    ts = int(dt.timestamp() * 1000)

    return ts


def millis_to_datetime(millis: int) -> datetime:
    """
    Converts a millisecond unix timestamp to a datetime object with no (i.e. utc) timezone
    :param millis: millisecond resolution unix timestamp
    :return: datetime with no (i.e. utc) timezone
    """
    return datetime.utcfromtimestamp(millis / 1000)
