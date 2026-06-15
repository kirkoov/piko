from app.period import period_for_date


def test_period_start():
    start, end = period_for_date("2026-06-08")
    assert start == "2026-06-08"
    assert end == "2026-06-28"


def test_period_middle():
    start, end = period_for_date("2026-06-20")
    assert start == "2026-06-08"
    assert end == "2026-06-28"


def test_next_period():
    start, end = period_for_date("2026-06-29")
    assert start == "2026-06-29"
    assert end == "2026-07-19"


def test_last_day_of_period():
    start, end = period_for_date("2026-06-28")
    assert start == "2026-06-08"
    assert end == "2026-06-28"
