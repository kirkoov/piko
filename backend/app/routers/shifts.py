from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_session import get_current_user
from app.config import API_PREFIX
from app.dependencies import get_db
from app.models import Session, Shift, User
from app.serializers import shift_to_dict

router = APIRouter(
    prefix=f"{API_PREFIX}/shifts",
    tags=["Shifts"],
)


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
