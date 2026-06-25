from app.balance import calculate_balance
from app.models import Shift
from app.period import group_shifts_by_period


def test_balance_deducts_early_leave():
    shift = Shift(
        planned_start="08:00",
        planned_end="16:00",
        actual_start="08:00",
        actual_end="15:00",
    )
    assert calculate_balance(0, [shift]) == -60


def test_balance_ignores_positive_overtime():
    shift = Shift(
        planned_start="08:00",
        planned_end="16:00",
        actual_start="08:00",
        actual_end="17:00",
    )
    assert calculate_balance(0, [shift]) == 0


def test_balance_adds_evening_bonus():
    shift = Shift(
        planned_start="14:00",
        planned_end="22:00",
        actual_start="14:00",
        actual_end="22:00",
    )
    assert calculate_balance(0, [shift]) == 32


def test_balance_adds_morning_bonus():
    shift = Shift(
        planned_start="05:00",
        planned_end="07:00",
        actual_start="05:00",
        actual_end="07:00",
    )
    assert calculate_balance(0, [shift]) == 36


def test_balance_combines_deduction_and_bonus():
    shift = Shift(
        planned_start="14:00",
        planned_end="22:00",
        actual_start="14:00",
        actual_end="21:00",
    )
    assert calculate_balance(0, [shift]) == -36


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
    assert periods[1]["shift_count"] == 1


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
