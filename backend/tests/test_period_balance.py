from app.period import group_shifts_by_period


def test_group_shifts_by_period():
    shifts = [
        {
            "date": "2026-06-08",
            "delta_minutes": 0,
            "morning_bonus": 0,
            "evening_bonus": 28,
        },
        {
            "date": "2026-06-09",
            "delta_minutes": 45,
            "morning_bonus": 0,
            "evening_bonus": 28,
        },
        {
            "date": "2026-06-29",
            "delta_minutes": 0,
            "morning_bonus": 0,
            "evening_bonus": 24,
        },
    ]

    periods = group_shifts_by_period(shifts)

    assert len(periods) == 2

    assert periods[0]["period_start"] == "2026-06-08"
    assert periods[0]["period_end"] == "2026-06-28"

    assert periods[1]["period_start"] == "2026-06-29"
    assert periods[1]["period_end"] == "2026-07-19"


def test_period_balance():
    shifts = [
        {
            "date": "2026-06-08",
            "delta_minutes": 0,
            "morning_bonus": 0,
            "evening_bonus": 28,
        },
        {
            "date": "2026-06-09",
            "delta_minutes": 45,
            "morning_bonus": 0,
            "evening_bonus": 28,
        },
    ]
    periods = group_shifts_by_period(shifts)
    assert periods[0]["period_start"] == "2026-06-08"
    assert periods[0]["balance_minutes"] == 101


def test_multiple_period_balances():
    shifts = [
        {
            "date": "2026-06-08",
            "delta_minutes": 0,
            "morning_bonus": 0,
            "evening_bonus": 28,
        },
        {
            "date": "2026-06-09",
            "delta_minutes": 45,
            "morning_bonus": 0,
            "evening_bonus": 28,
        },
        {
            "date": "2026-06-29",
            "delta_minutes": 0,
            "morning_bonus": 0,
            "evening_bonus": 24,
        },
    ]
    periods = group_shifts_by_period(shifts)
    assert periods[0]["balance_minutes"] == 101
    assert periods[1]["balance_minutes"] == 24
