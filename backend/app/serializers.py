from app.models import Shift
from app.period import period_for_date
from app.timecalc import (
    duration,
    evening_bonus,
    morning_bonus,
    recommended_shift,
    shift_difference,
)


def shift_to_dict(s: Shift) -> dict:
    period_start, period_end = period_for_date(
        s.date,
    )

    return {
        "id": s.id,
        "date": s.date,
        "period_start": period_start,
        "period_end": period_end,
        "planned": f"{s.planned_start}-{s.planned_end}",
        "actual": f"{s.actual_start}-{s.actual_end}",
        "planned_minutes": duration(
            s.planned_start,
            s.planned_end,
        ),
        "actual_minutes": duration(
            s.actual_start,
            s.actual_end,
        ),
        "delta_minutes": shift_difference(
            s.planned_start,
            s.planned_end,
            s.actual_start,
            s.actual_end,
        ),
        "morning_bonus": morning_bonus(
            s.actual_start,
            s.actual_end,
        ),
        "evening_bonus": evening_bonus(
            s.actual_start,
            s.actual_end,
        ),
        "latest_child_name": s.latest_child_name,
        "latest_child_time": s.latest_child_time,
        "note": s.note,
        "recommended_shift": recommended_shift(
            s.planned_start,
            s.planned_end,
            s.latest_child_time,
        ),
    }
