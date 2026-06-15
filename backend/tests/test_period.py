from app.period import period_for_date, shifts_in_period


def test_period_start():
    assert period_for_date("2026-06-08") == ("2026-06-08", "2026-06-28")


def test_period_middle():
    assert period_for_date("2026-06-20") == ("2026-06-08", "2026-06-28")


def test_next_period():
    assert period_for_date("2026-06-29") == ("2026-06-29", "2026-07-19")


def test_last_day_of_period():
    assert period_for_date("2026-06-28") == ("2026-06-08", "2026-06-28")


def test_shifts_in_period():
    shifts = [
        {"date": "2026-06-05"},
        {"date": "2026-06-08"},
        {"date": "2026-06-15"},
        {"date": "2026-06-28"},
        {"date": "2026-06-29"},
    ]

    result = shifts_in_period(
        shifts,
        "2026-06-20",
    )

    assert len(result) == 3
    assert result[0]["date"] == "2026-06-08"
    assert result[1]["date"] == "2026-06-15"
    assert result[2]["date"] == "2026-06-28"


def test_empty_period():
    shifts = [
        {"date": "2026-05-01"},
        {"date": "2026-05-15"},
    ]
    result = shifts_in_period(
        shifts,
        "2026-06-20",
    )
    assert result == []


def test_period_boundaries():
    shifts = [
        {"date": "2026-06-08"},
        {"date": "2026-06-28"},
    ]
    result = shifts_in_period(
        shifts,
        "2026-06-20",
    )
    assert result == [{"date": "2026-06-08"}, {"date": "2026-06-28"}]
