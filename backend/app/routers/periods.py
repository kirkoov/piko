from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_session import get_current_user
from app.config import API_PREFIX
from app.dependencies import get_db
from app.models import Session, Shift, User
from app.period import group_shifts_by_period, period_for_date, shifts_in_period
from app.serializers import shift_to_dict

router = APIRouter(
    prefix=f"{API_PREFIX}/periods",
    tags=["Periods"],
)


@router.get("")
async def list_periods(
    auth: tuple[User, Session] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    user, _ = auth
    result = await db.execute(
        select(Shift).where(Shift.user_id == user.id).order_by(Shift.date)
    )
    shifts = result.scalars().all()
    shift_dicts = [shift_to_dict(s) for s in shifts]

    return group_shifts_by_period(shift_dicts)


@router.get("/current")
async def current_period(
    auth: tuple[User, Session] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:

    user, _ = auth
    result = await db.execute(
        select(Shift).where(Shift.user_id == user.id).order_by(Shift.date)
    )

    shifts = result.scalars().all()

    today = date.today().isoformat()
    start, end = period_for_date(today)
    shift_dicts = [shift_to_dict(s) for s in shifts]

    current_shifts = shifts_in_period(
        shift_dicts,
        today,
    )

    return {
        "period_start": start,
        "period_end": end,
        "shifts": current_shifts,
    }
