from datetime import datetime
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("America/Vancouver")


def today() -> datetime:
    return datetime.now(tz=TIMEZONE)
