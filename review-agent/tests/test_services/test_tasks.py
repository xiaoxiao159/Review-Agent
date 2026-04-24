from unittest.mock import AsyncMock

import pytest

from app.services.tasks import _parse_date_range


def test_parse_date_range_handles_none():
    start, end = _parse_date_range(None)
    assert start is None
    assert end is None


def test_parse_date_range_parses_iso_dates():
    start, end = _parse_date_range({"start": "2026-01-01", "end": "2026-01-31"})
    assert str(start) == "2026-01-01"
    assert str(end) == "2026-01-31"
