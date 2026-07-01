from contextlib import asynccontextmanager
from datetime import date, datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_session import get_current_user
from app.balance import calculate_balance
from app.config import DATE_FORMAT
from app.database import engine
from app.dependencies import get_db
from app.models import Base, Session, Shift, User
from app.period import group_shifts_by_period, period_for_date, shifts_in_period
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.timecalc import (
    duration,
    evening_bonus,
    morning_bonus,
    recommended_shift,
    shift_difference,
)
from app.validators import validate_shift_data

BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
PROJECT_ROOT = BASE_DIR.parent  # piko/
FRONTEND_DIR = PROJECT_ROOT / "frontend"


class ShiftUpdate(BaseModel):
    planned_start: str
    planned_end: str
    actual_start: str
    actual_end: str
    latest_child_name: str
    latest_child_time: str
    note: str = ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # shutdown (optional cleanup)
    await engine.dispose()


app = FastAPI(title="Piko", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(users_router)


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


@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    auth: tuple[User, Session] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:

    current_user, _ = auth
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required",
        )
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Admin cannot delete themselves",
        )

    await db.delete(user)
    await db.commit()

    return {
        "status": "deleted",
        "id": user.id,
    }


@app.post("/shifts")
async def create_shift(
    date: str,
    planned_start: str,
    planned_end: str,
    actual_start: str,
    actual_end: str,
    latest_child_name: str,
    latest_child_time: str,
    note: str = "",
    auth: tuple[User, Session] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:

    user, _ = auth

    try:
        datetime.strptime(date, DATE_FORMAT)
    except ValueError:
        raise HTTPException(400, "Invalid date")

    validate_shift_data(
        planned_start,
        planned_end,
        actual_start,
        actual_end,
        latest_child_time,
    )

    # CHECK EXISTING SHIFT
    result = await db.execute(
        select(Shift).where(Shift.user_id == user.id, Shift.date == date)
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
        date=date,
        planned_start=planned_start,
        planned_end=planned_end,
        actual_start=actual_start,
        actual_end=actual_end,
        latest_child_name=latest_child_name,
        latest_child_time=latest_child_time,
        note=note,
    )

    db.add(shift)

    await db.commit()
    await db.refresh(shift)

    return {
        "status": "created",
        "shift_id": shift.id,
    }


@app.get("/shifts")
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


@app.put("/shifts/{shift_id}")
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


@app.delete("/shifts/{shift_id}")
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


@app.get("/balance")
async def get_balance(
    auth: tuple[User, Session] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user, _ = auth
    result = await db.execute(select(Shift).where(Shift.user_id == user.id))
    shifts = result.scalars().all()
    balance = calculate_balance(
        user.starting_balance_minutes,
        shifts,
    )

    return {
        "user_id": user.id,
        "balance_minutes": balance,
    }


@app.get("/current-period")
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


@app.get("/periods")
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


app.mount(
    "/",
    StaticFiles(directory=str(FRONTEND_DIR), html=True),
    name="frontend",
)
