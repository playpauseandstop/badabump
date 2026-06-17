import datetime

UTC = datetime.timezone.utc


def utcnow_naive() -> datetime.datetime:
    """Replacement for now deprecated datetime.datetime.utcnow function.

    To return current datetime at UTC timezone, but without TZ info (naive).
    """
    return datetime.datetime.now(UTC).replace(tzinfo=None)
