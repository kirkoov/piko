from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_password
from app.auth_session import get_current_user
from app.config import API_PREFIX, SESSION_LIFETIME
from app.dependencies import get_db
from app.models import Session, User

router = APIRouter(
    prefix=f"{API_PREFIX}/auth",
    tags=["Authentication"],
)


@router.post("/login")
async def login(
    name: str,
    password: str,
    db: AsyncSession = Depends(get_db),
):

    print(f"LOGIN REQUEST: name={name!r} password={password!r}")

    result = await db.execute(select(User).where(User.name == name))

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = str(uuid4())

    session = Session(
        token=token,
        user_id=user.id,
        created=datetime.now(timezone.utc),
        expires=datetime.now(timezone.utc) + SESSION_LIFETIME,
    )

    db.add(session)
    await db.commit()

    return {
        "status": "ok",
        "access_token": token,
        "token_type": "Bearer",
        "user_id": user.id,
        "name": user.name,
        "is_admin": user.is_admin,
    }


@router.post("/logout")
async def logout(
    auth: tuple[User, Session] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _, session = auth
    await db.delete(session)
    await db.commit()
    return {"status": "ok"}


@router.get("/me")
async def me(
    auth: tuple[User, Session] = Depends(get_current_user),
):
    user, _ = auth

    return {
        "user_id": user.id,
        "name": user.name,
        "is_admin": user.is_admin,
    }
