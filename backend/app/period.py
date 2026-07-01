from collections import defaultdict
from datetime import date, datetime, timedelta

from app.config import DATE_FORMAT, PAY_PERIOD_LENGTH, PAY_PERIOD_START_DAY

PERIOD_START = date(2026, 6, PAY_PERIOD_START_DAY)


def period_for_date(date_str: str) -> tuple[str, str]:
    target = datetime.strptime(
        date_str,
        DATE_FORMAT,
    ).date()

    days = (target - PERIOD_START).days

    period_index = days // PAY_PERIOD_LENGTH

    start = PERIOD_START + timedelta(
        days=period_index * PAY_PERIOD_LENGTH,
    )

    end = start + timedelta(
        days=PAY_PERIOD_LENGTH - 1,
    )

    return (
        start.isoformat(),
        end.isoformat(),
    )


def shifts_in_period(
    shifts: list[dict],
    date_str: str,
) -> list[dict]:

    start, end = period_for_date(date_str)
    result = []
    for shift in shifts:
        shift_date = shift["date"]
        if start <= shift_date <= end:
            result.append(shift)
    return result


def group_shifts_by_period(shifts) -> list[dict]:
    groups = defaultdict(list)
    for shift in shifts:
        start, end = period_for_date(shift["date"])
        groups[(start, end)].append(shift)

    result = []
    for (start, end), period_shifts in sorted(groups.items()):
        balance = sum(
            s["delta_minutes"] + s["morning_bonus"] + s["evening_bonus"]
            for s in period_shifts
        )
        result.append(
            {
                "period_start": start,
                "period_end": end,
                "balance_minutes": balance,
                "shift_count": len(period_shifts),
                "shifts": period_shifts,
            }
        )
    return result
