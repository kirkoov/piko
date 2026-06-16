from collections import defaultdict
from datetime import date, datetime, timedelta

PERIOD_START = date(2026, 6, 8)
PERIOD_LENGTH = 21


def period_for_date(date_str: str) -> tuple[str, str]:
    target = datetime.strptime(
        date_str,
        "%Y-%m-%d",
    ).date()

    days = (target - PERIOD_START).days

    period_index = days // PERIOD_LENGTH

    start = PERIOD_START + timedelta(
        days=period_index * PERIOD_LENGTH,
    )

    end = start + timedelta(
        days=PERIOD_LENGTH - 1,
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


def group_shifts_by_period(shifts):
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
                "shifts": period_shifts,
            }
        )
    return result
