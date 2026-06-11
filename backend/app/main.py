from contextlib import asynccontextmanager

# from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionLocal, engine
from app.models import Base, Shift, User
from app.timecalc import duration, morning_bonus, recommended_shift, shift_difference

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # shutdown (optional cleanup)
    await engine.dispose()


app = FastAPI(title="Piko", lifespan=lifespan)


async def get_db():
    async with SessionLocal() as session:
        yield session


@app.post("/users")
async def create_user(
    name: str,
    db: AsyncSession = Depends(get_db),
) -> dict:

    user = User(name=name)
    db.add(user)

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()
        return {"status": "error", "message": f"User '{name}' already exists"}

    return {"status": "created", "name": name}


@app.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(User))
    users = result.scalars().all()

    return [{"id": u.id, "name": u.name} for u in users]


@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()

    return {"status": "deleted", "id": user_id}


@app.post("/shifts")
async def create_shift(
    user_id: int,
    date: str,
    planned_start: str,
    planned_end: str,
    actual_start: str,
    actual_end: str,
    latest_child_name: str,
    latest_child_time: str,
    db: AsyncSession = Depends(get_db),
) -> dict:

    # CHECK EXISTING SHIFT
    result = await db.execute(
        select(Shift).where(Shift.user_id == user_id, Shift.date == date)
    )

    existing = result.scalars().first()

    if existing:
        return {
            "status": "error",
            "message": "Shift already exists for this user & latest child on this date",
            "shift_id": existing.id,
        }

    shift = Shift(
        user_id=user_id,
        date=date,
        planned_start=planned_start,
        planned_end=planned_end,
        actual_start=actual_start,
        actual_end=actual_end,
        latest_child_name=latest_child_name,
        latest_child_time=latest_child_time,
    )

    db.add(shift)
    await db.commit()

    diff = shift_difference(
        planned_start,
        planned_end,
        actual_start,
        actual_end,
    )

    return {"status": "created", "overtime_minutes": diff}


@app.get("/shifts")
async def list_shifts(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:

    result = await db.execute(
        select(Shift).where(Shift.user_id == user_id).order_by(Shift.date)
    )

    shifts = result.scalars().all()

    return [
        {
            "id": s.id,
            "date": s.date,
            # "display_date": d.strftime("%d.%m.%Y"),
            # "weekday": d.strftime("%A"),
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
            "latest_child_name": s.latest_child_name,
            "latest_child_time": s.latest_child_time,
            "note": s.note,
            "recommended_shift": recommended_shift(
                s.planned_start,
                s.planned_end,
                s.latest_child_time,
            ),
        }
        for s in shifts
        # for d in [datetime.strptime(s.date, "%Y-%m-%d")]
    ]


@app.put("/shifts/{shift_id}")
async def update_shift(
    shift_id: int,
    data: ShiftUpdate,
    db: AsyncSession = Depends(get_db),
) -> dict:

    result = await db.execute(select(Shift).where(Shift.id == shift_id))

    shift = result.scalars().first()

    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    shift.planned_start = data.planned_start
    shift.planned_end = data.planned_end
    shift.actual_start = data.actual_start
    shift.actual_end = data.actual_end
    shift.latest_child_name = data.latest_child_name
    shift.latest_child_time = data.latest_child_time

    await db.commit()

    diff = shift_difference(
        shift.planned_start,
        shift.planned_end,
        shift.actual_start,
        shift.actual_end,
    )

    return {"status": "updated", "shift_id": shift_id, "overtime_minutes": diff}


@app.delete("/shifts/{shift_id}")
async def delete_shift(
    shift_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:

    result = await db.execute(select(Shift).where(Shift.id == shift_id))

    shift = result.scalars().first()

    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    await db.delete(shift)
    await db.commit()

    return {"status": "deleted", "shift_id": shift_id}


@app.get("/balance")
async def get_balance(user_id: int, db: AsyncSession = Depends(get_db)) -> dict:

    result = await db.execute(select(Shift).where(Shift.user_id == user_id))

    shifts = result.scalars().all()

    total = 0

    for s in shifts:
        total += shift_difference(
            s.planned_start,
            s.planned_end,
            s.actual_start,
            s.actual_end,
        )

        total += morning_bonus(
            s.actual_start,
            s.actual_end,
        )

    # starting_balance = 0  # later: from DB or payroll system
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return {
        "user_id": user_id,
        "balance_minutes": user.starting_balance_minutes + total,
    }


app.mount(
    "/",
    StaticFiles(directory=str(FRONTEND_DIR), html=True),
    name="frontend",
)
