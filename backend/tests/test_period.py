from app.period import period_for_date


def test_period_start():
    assert period_for_date("2026-06-08") == ("2026-06-08", "2026-06-28")


def test_period_middle():
    assert period_for_date("2026-06-20") == ("2026-06-08", "2026-06-28")


def test_next_period():
    assert period_for_date("2026-06-29") == ("2026-06-29", "2026-07-19")


def test_last_day_of_period():
    assert period_for_date("2026-06-28") == ("2026-06-08", "2026-06-28")
