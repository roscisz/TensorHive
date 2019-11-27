from datetime import datetime
import time


def utc2local(utc: datetime) -> datetime:
    """Converts UTC time to local."""
    epoch = time.mktime(utc.timetuple())
    offset = datetime.fromtimestamp(epoch) - datetime.utcfromtimestamp(epoch)
    return utc + offset
