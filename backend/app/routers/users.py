from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import hash_password
from app.config import API_PREFIX
from app.dependencies import get_db
from app.models import User

router = APIRouter(
    prefix=f"{API_PREFIX}/users",
    tags=["Users"],
)


@router.get("")
async def list_users(
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    result = await db.execute(select(User))
    users = result.scalars().all()

    return [{"id": u.id, "name": u.name} for u in users]


@router.post("")
async def create_user(
    name: str,
    password: str,
    db: AsyncSession = Depends(get_db),
) -> dict:

    user = User(
        name=name,
        password_hash=hash_password(password),
    )
    db.add(user)

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()
        return {"status": "error", "message": f"User '{name}' already exists"}

    return {"status": "created", "name": name}
