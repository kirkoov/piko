from datetime import datetime


def to_minutes(t: str) -> int:
    h, m = map(int, t.split(":"))
    return h * 60 + m


def shift_difference(
    planned_start: str, planned_end: str, actual_start: str, actual_end: str
) -> int:
    planned = duration(planned_start, planned_end)
    actual = duration(actual_start, actual_end)
    return actual - planned


def format_minutes(minutes: int) -> str:
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m"


def duration(start: str, end: str) -> int:
    fmt = "%H:%M"

    start_dt = datetime.strptime(start, fmt)
    end_dt = datetime.strptime(end, fmt)

    return int((end_dt - start_dt).total_seconds() // 60)
