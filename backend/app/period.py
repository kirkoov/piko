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
