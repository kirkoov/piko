from collections import defaultdict
from collections.abc import Sequence

from app.models import Shift
from app.period import period_for_date
from app.timecalc import (
    evening_compensation,
    evening_minutes,
    morning_bonus,
    shift_difference,
)


def calculate_balance(
    starting_balance: int,
    shifts: Sequence[Shift],
) -> int:

    total = starting_balance

    periods = defaultdict(list)

    for shift in shifts:
        start, end = period_for_date(shift.date)
        periods[(start, end)].append(shift)

    for period_shifts in periods.values():
        period_evening_minutes = 0

        for shift in period_shifts:
            total += shift_difference(
                shift.planned_start,
                shift.planned_end,
                shift.actual_start,
                shift.actual_end,
            )

            total += morning_bonus(
                shift.actual_start,
                shift.actual_end,
            )

            period_evening_minutes += evening_minutes(
                shift.actual_start,
                shift.actual_end,
            )

        total += evening_compensation(period_evening_minutes)

    return total
