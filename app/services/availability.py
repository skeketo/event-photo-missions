import os
from datetime import datetime
from zoneinfo import ZoneInfo


def uploads_open_at():
    value = os.getenv("UPLOADS_OPEN_AT", "")
    timezone = os.getenv("TIMEZONE", "Europe/Madrid")

    if not value:
        return None

    try:
        dt = datetime.fromisoformat(value)
        return dt.replace(tzinfo=ZoneInfo(timezone))
    except Exception:
        return None


def uploads_are_open():
    open_at = uploads_open_at()

    if open_at is None:
        return True

    now = datetime.now(open_at.tzinfo)
    return now >= open_at


def uploads_open_message():
    open_at = uploads_open_at()

    if open_at is None:
        return ""

    return open_at.strftime("%d/%m/%Y a las %H:%M")
