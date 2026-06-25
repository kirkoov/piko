from collections.abc import Sequence

from app.models import Shift
from app.timecalc import evening_bonus, morning_bonus, shift_difference


def calculate_balance(
    starting_balance: int,
    shifts: Sequence[Shift],
) -> int:

    total = starting_balance

    for s in shifts:
        difference = shift_difference(
            s.planned_start,
            s.planned_end,
            s.actual_start,
            s.actual_end,
        )

        # Deduct early departures only
        if difference < 0:
            total += difference

        total += morning_bonus(
            s.actual_start,
            s.actual_end,
        )

        total += evening_bonus(
            s.actual_start,
            s.actual_end,
        )

    return total
