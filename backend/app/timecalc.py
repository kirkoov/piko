from datetime import datetime

MORNING_BONUS_MULTIPLIER = 9
SHIFT_DIV_MIN = 30


def overlap_minutes(
    start: str,
    end: str,
    period_start: str,
    period_end: str,
) -> int:

    fmt = "%H:%M"

    work_start = datetime.strptime(start, fmt)
    work_end = datetime.strptime(end, fmt)

    bonus_start = datetime.strptime(period_start, fmt)
    bonus_end = datetime.strptime(period_end, fmt)

    overlap_start = max(work_start, bonus_start)
    overlap_end = min(work_end, bonus_end)

    if overlap_end <= overlap_start:
        return 0

    return int((overlap_end - overlap_start).total_seconds() // 60)


def morning_bonus(actual_start: str, actual_end: str) -> int:
    minutes = overlap_minutes(
        actual_start,
        actual_end,
        "05:00",
        "07:00",
    )
    completed_blocks = minutes // SHIFT_DIV_MIN
    return completed_blocks * MORNING_BONUS_MULTIPLIER


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
