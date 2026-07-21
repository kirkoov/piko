from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import hash_password
from app.auth_session import require_admin
from app.config import API_PREFIX
from app.dependencies import get_db
from app.models import Session, User

router = APIRouter(
    prefix=f"{API_PREFIX}/users",
    tags=["Users"],
)


@router.get("")
async def list_users(
    _: tuple[User, Session] = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    result = await db.execute(select(User))
    users = result.scalars().all()

    return [{"id": u.id, "name": u.name} for u in users]


@router.post("")
async def create_user(
    name: str,
    password: str,
    _: tuple[User, Session] = Depends(require_admin),
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

    return {"status": "created", "id": user.id, "name": name}


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    auth: tuple[User, Session] = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:

    current_user, _ = auth

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


@router.put("/{user_id}/password")
async def change_user_password(
    user_id: int,
    password: str,
    _: tuple[User, Session] = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if not password:
        raise HTTPException(
            status_code=400,
            detail="Password cannot be empty",
        )

    user.password_hash = hash_password(password)

    await db.commit()

    return {
        "status": "password changed",
        "id": user.id,
    }
