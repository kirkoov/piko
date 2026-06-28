from datetime import datetime, timezone

from fastapi import HTTPException, Request
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Session, User


def to_utc(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


async def get_current_user(request: Request) -> tuple[User, Session]:
    auth = request.headers.get("Authorization")

    if auth is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    scheme, sep, token = auth.partition(" ")

    if sep == "":
        raise HTTPException(status_code=401, detail="Malformed Authorization header")

    if scheme != "Bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")

    async with SessionLocal() as db:
        session_result = await db.execute(select(Session).where(Session.token == token))
        session = session_result.scalar_one_or_none()

        if session is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # if session.expires < datetime.now(timezone.utc):
        #     raise HTTPException(status_code=401, detail="Session expired")

        if to_utc(session.expires) < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Session expired")

        user_result = await db.execute(select(User).where(User.id == session.user_id))
        user = user_result.scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user, session
