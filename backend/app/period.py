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
    start_dt = datetime.strptime(start, "%Y-%m-%d").date()
    end_dt = datetime.strptime(end, "%Y-%m-%d").date()

    result = []

    for shift in shifts:
        shift_date = datetime.strptime(
            shift["date"],
            "%Y-%m-%d",
        ).date()

        if start_dt <= shift_date <= end_dt:
            result.append(shift)

    return result
