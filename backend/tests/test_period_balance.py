from decimal import Decimal

from app.balance import calculate_balance
from app.models import Shift
from app.period import group_shifts_by_period
from app.timecalc import evening_compensation_exact


def make_shift(
    date="2026-06-08",
    planned_start="08:00",
    planned_end="16:00",
    actual_start="08:00",
    actual_end="16:00",
):
    return Shift(
        date=date,
        planned_start=planned_start,
        planned_end=planned_end,
        actual_start=actual_start,
        actual_end=actual_end,
    )


def test_balance_deducts_early_leave():
    shift = make_shift(actual_end="15:00")
    assert calculate_balance(0, [shift]) == -60


def test_balance_counts_positive_shift_difference():
    shift = make_shift(actual_end="17:00")
    assert calculate_balance(0, [shift]) == 60


def test_balance_adds_morning_bonus():
    shift = make_shift(
        planned_start="05:00",
        planned_end="07:00",
        actual_start="05:00",
        actual_end="07:00",
    )
    assert calculate_balance(0, [shift]) == 36


def test_balance_combines_deduction_and_evening_compensation():
    shift = make_shift(
        planned_start="14:00",
        planned_end="22:00",
        actual_start="14:00",
        actual_end="21:00",
    )
    assert calculate_balance(0, [shift]) == -33


def test_group_shifts_by_period():
    shifts = [
        {
            "date": "2026-06-08",
            "delta_minutes": 0,
            "morning_bonus": 0,
            "evening_bonus": 28,
            "evening_minutes": 210,
        },
        {
            "date": "2026-06-09",
            "delta_minutes": 45,
            "morning_bonus": 0,
            "evening_bonus": 28,
            "evening_minutes": 210,
        },
        {
            "date": "2026-06-29",
            "delta_minutes": 0,
            "morning_bonus": 0,
            "evening_bonus": 24,
            "evening_minutes": 180,
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
            "evening_minutes": 210,
        },
        {
            "date": "2026-06-09",
            "delta_minutes": 45,
            "morning_bonus": 0,
            "evening_bonus": 28,
            "evening_minutes": 180,
        },
    ]

    periods = group_shifts_by_period(shifts)

    assert periods[0]["period_start"] == "2026-06-08"
    # assert periods[0]["balance_minutes"] == 101
    assert periods[0]["balance_minutes"] == 103
    assert periods[0]["evening_minutes"] == 390
    # assert periods[0]["evening_compensation_minutes"] == 58.5
    assert periods[0]["evening_compensation_minutes"] == 58
    assert periods[0]["evening_compensation_exact_minutes"] == Decimal("58.50")


def test_multiple_period_balances():
    shifts = [
        {
            "date": "2026-06-08",
            "delta_minutes": 0,
            "morning_bonus": 0,
            "evening_bonus": 28,
            "evening_minutes": 210,
        },
        {
            "date": "2026-06-09",
            "delta_minutes": 45,
            "morning_bonus": 0,
            "evening_bonus": 28,
            "evening_minutes": 210,
        },
        {
            "date": "2026-06-29",
            "delta_minutes": 0,
            "morning_bonus": 0,
            "evening_bonus": 24,
            "evening_minutes": 180,
        },
    ]
    periods = group_shifts_by_period(shifts)
    # assert periods[0]["balance_minutes"] == 101
    # assert periods[1]["balance_minutes"] == 24
    assert periods[0]["balance_minutes"] == 108
    assert periods[1]["balance_minutes"] == 27


def test_period_evening_minutes():
    shifts = [
        {
            "date": "2026-06-08",
            "delta_minutes": 0,
            "morning_bonus": 0,
            "evening_bonus": 28,
            "evening_minutes": 210,
        },
        {
            "date": "2026-06-09",
            "delta_minutes": 45,
            "morning_bonus": 0,
            "evening_bonus": 28,
            "evening_minutes": 180,
        },
    ]

    periods = group_shifts_by_period(shifts)

    assert periods[0]["evening_minutes"] == 390


def test_balance_adds_evening_compensation():
    shift = make_shift(
        planned_start="14:00",
        planned_end="22:00",
        actual_start="14:00",
        actual_end="22:00",
    )
    assert calculate_balance(0, [shift]) == 36


def test_balance_applies_evening_compensation_per_period():
    shifts = [
        make_shift(
            date="2026-06-08",
            planned_start="18:00",
            planned_end="21:30",
            actual_start="18:00",
            actual_end="21:30",
        ),
        make_shift(
            date="2026-06-29",
            planned_start="18:00",
            planned_end="21:30",
            actual_start="18:00",
            actual_end="21:30",
        ),
    ]

    assert calculate_balance(0, shifts) == 62


def test_employer_period_reconstruction():
    base_difference = Decimal("-61")
    evening = evening_compensation_exact(1203)
    night = Decimal("27")
    overtime = Decimal("21") * Decimal("0.50")

    total = base_difference + evening + night + overtime

    assert evening == Decimal("180.45")
    assert overtime == Decimal("10.50")
    assert total == Decimal("156.95")
