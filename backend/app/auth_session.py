from datetime import datetime, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Session, User

bearer_scheme = HTTPBearer(auto_error=False)


def to_utc(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> tuple[User, Session]:

    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    scheme = credentials.scheme
    token = credentials.credentials

    if scheme != "Bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")

    async with SessionLocal() as db:
        session_result = await db.execute(select(Session).where(Session.token == token))
        session = session_result.scalar_one_or_none()

        if session is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        if to_utc(session.expires) < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Session expired")

        user_result = await db.execute(select(User).where(User.id == session.user_id))
        user = user_result.scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user, session


async def require_admin(
    auth: tuple[User, Session] = Depends(get_current_user),
) -> tuple[User, Session]:
    user, session = auth

    if not user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required",
        )

    return user, session
