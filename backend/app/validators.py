import re

from fastapi import HTTPException

from app.timecalc import to_minutes

TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def validate_time(value: str) -> bool:
    return bool(TIME_RE.match(value))


def validate_shift_data(
    planned_start,
    planned_end,
    actual_start,
    actual_end,
    latest_child_time,
):
    if not validate_time(planned_start):
        raise HTTPException(400, "Invalid planned_start")

    if not validate_time(planned_end):
        raise HTTPException(400, "Invalid planned_end")

    if not validate_time(actual_start):
        raise HTTPException(400, "Invalid actual_start")

    if not validate_time(actual_end):
        raise HTTPException(400, "Invalid actual_end")

    if not validate_time(latest_child_time):
        raise HTTPException(400, "Invalid latest_child_time")

    if to_minutes(planned_end) <= to_minutes(planned_start):
        raise HTTPException(
            400,
            "Planned shift end must be after start",
        )

    if to_minutes(actual_end) <= to_minutes(actual_start):
        raise HTTPException(
            400,
            "Actual shift end must be after start",
        )
