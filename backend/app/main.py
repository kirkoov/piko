from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import engine
from app.models import Base
from app.routers.auth import router as auth_router
from app.routers.balance import router as balance_router
from app.routers.periods import router as periods_router
from app.routers.shifts import router as shifts_router
from app.routers.users import router as users_router

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
app.include_router(balance_router)
app.include_router(periods_router)


app.mount(
    "/",
    StaticFiles(directory=str(FRONTEND_DIR), html=True),
    name="frontend",
)
