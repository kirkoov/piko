from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_session import get_current_user
from app.balance import calculate_balance
from app.database import engine
from app.dependencies import get_db
from app.models import Base, Session, Shift, User
from app.period import group_shifts_by_period, period_for_date, shifts_in_period
from app.routers.auth import router as auth_router
from app.routers.shifts import router as shifts_router
from app.routers.users import router as users_router
from app.serializers import shift_to_dict

BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
PROJECT_ROOT = BASE_DIR.parent  # piko/
FRONTEND_DIR = PROJECT_ROOT / "frontend"


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
app.include_router(shifts_router)


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
