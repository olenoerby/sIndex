import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from api.utils import parse_retry_after_seconds
from datetime import datetime, timedelta


def test_parse_seconds():
    assert parse_retry_after_seconds('5') == 5
    assert parse_retry_after_seconds(' 10 ') == 10


def test_parse_http_date():
    # create a date 30 seconds in the future
    future = (datetime.utcnow() + timedelta(seconds=30)).strftime('%a, %d %b %Y %H:%M:%S GMT')
    secs = parse_retry_after_seconds(future)
    assert isinstance(secs, int)
    assert secs >= 29


def test_parse_invalid():
    assert parse_retry_after_seconds('not-a-date') is None
    assert parse_retry_after_seconds('') is None
