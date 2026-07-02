from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_session import get_current_user
from app.config import API_PREFIX, DATE_FORMAT
from app.dependencies import get_db
from app.models import Session, Shift, User
from app.schemas import ShiftCreate, ShiftUpdate
from app.serializers import shift_to_dict
from app.validators import validate_shift_data

router = APIRouter(
    prefix=f"{API_PREFIX}/shifts",
    tags=["Shifts"],
)


@router.post("")
async def create_shift(
    data: ShiftCreate,
    auth: tuple[User, Session] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:

    user, _ = auth

    try:
        datetime.strptime(data.date, DATE_FORMAT)
    except ValueError:
        raise HTTPException(400, "Invalid date")

    validate_shift_data(
        data.planned_start,
        data.planned_end,
        data.actual_start,
        data.actual_end,
        data.latest_child_time,
    )

    # CHECK EXISTING SHIFT
    result = await db.execute(
        select(Shift).where(Shift.user_id == user.id, Shift.date == data.date)
    )

    existing = result.scalars().first()

    if existing:
        return {
            "status": "error",
            "message": "Shift already exists for this user on this date",
            "shift_id": existing.id,
        }

    shift = Shift(
        user_id=user.id,
        date=data.date,
        planned_start=data.planned_start,
        planned_end=data.planned_end,
        actual_start=data.actual_start,
        actual_end=data.actual_end,
        latest_child_name=data.latest_child_name,
        latest_child_time=data.latest_child_time,
        note=data.note,
    )

    db.add(shift)

    await db.commit()
    await db.refresh(shift)

    return {
        "status": "created",
        "shift_id": shift.id,
    }


@router.get("")
async def list_shifts(
    auth: tuple[User, Session] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:

    user, _ = auth
    result = await db.execute(
        select(Shift).where(Shift.user_id == user.id).order_by(Shift.date)
    )

    shifts = result.scalars().all()

    return [shift_to_dict(s) for s in shifts]


@router.put("/{shift_id}")
async def update_shift(
    shift_id: int,
    data: ShiftUpdate,
    auth: tuple[User, Session] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:

    user, _ = auth

    result = await db.execute(
        select(Shift).where(
            Shift.id == shift_id,
            Shift.user_id == user.id,
        )
    )

    shift = result.scalars().first()

    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    validate_shift_data(
        data.planned_start,
        data.planned_end,
        data.actual_start,
        data.actual_end,
        data.latest_child_time,
    )

    shift.planned_start = data.planned_start
    shift.planned_end = data.planned_end
    shift.actual_start = data.actual_start
    shift.actual_end = data.actual_end
    shift.latest_child_name = data.latest_child_name
    shift.latest_child_time = data.latest_child_time
    shift.note = data.note

    await db.commit()

    return {"status": "updated", "shift_id": shift_id}


@router.delete("/{shift_id}")
async def delete_shift(
    shift_id: int,
    auth: tuple[User, Session] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:

    user, _ = auth
    result = await db.execute(
        select(Shift).where(
            Shift.id == shift_id,
            Shift.user_id == user.id,
        )
    )

    shift = result.scalar_one_or_none()

    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    await db.delete(shift)
    await db.commit()

    return {"status": "deleted", "shift_id": shift_id}
