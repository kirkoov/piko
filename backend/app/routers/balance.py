from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_session import get_current_user
from app.balance import calculate_balance
from app.config import API_PREFIX
from app.dependencies import get_db
from app.models import Session, Shift, User

router = APIRouter(
    prefix=f"{API_PREFIX}/balance",
    tags=["Balance"],
)


@router.get("")
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
