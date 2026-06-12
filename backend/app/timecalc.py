from datetime import datetime

MORNING_SHIFT_START = "05:00"
MORNING_SHIFT_END = "07:00"
EVENING_SHIFT_START = "18:00"
EVENING_SHIFT_END = "22:00"

MORNING_BONUS_MULTIPLIER = 9
EVENING_BONUS_MULTIPLIER = 4
SHIFT_DIV_MIN = 30


def recommended_shift(
    planned_start: str,
    planned_end: str,
    latest_child_time: str,
) -> str | None:

    if latest_child_time >= planned_end:
        return None

    planned_duration = duration(
        planned_start,
        planned_end,
    )

    latest = to_minutes(latest_child_time)

    new_start = latest - planned_duration

    hours = new_start // 60
    mins = new_start % 60

    start_str = f"{hours:02d}:{mins:02d}"

    return f"{start_str}-{latest_child_time}"


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
        MORNING_SHIFT_START,
        MORNING_SHIFT_END,
    )
    completed_blocks = minutes // SHIFT_DIV_MIN
    return completed_blocks * MORNING_BONUS_MULTIPLIER


def evening_bonus(actual_start: str, actual_end: str) -> int:
    minutes = overlap_minutes(
        actual_start,
        actual_end,
        EVENING_SHIFT_START,
        EVENING_SHIFT_END,
    )
    completed_blocks = minutes // SHIFT_DIV_MIN
    return completed_blocks * EVENING_BONUS_MULTIPLIER


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
