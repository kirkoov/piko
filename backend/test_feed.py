import asyncio

from app.database import SessionLocal
from app.models import Shift, User


async def main():
    async with SessionLocal() as db:
        user = User(
            name="Lora",
            starting_balance_minutes=36,
        )

        db.add(user)
        await db.flush()

        shifts = [
            ("2026-06-08", "13:30", "21:30", "Masha", "21:15"),
            ("2026-06-09", "14:30", "22:30", "Petya", "21:45"),
            ("2026-06-10", "14:15", "21:30", "Vanya", "21:00"),
            ("2026-06-11", "14:30", "22:30", "Sofia", "21:00"),
            ("2026-06-12", "14:30", "21:30", "Artem", "21:00"),
        ]

        for date, start, end, child, child_time in shifts:
            db.add(
                Shift(
                    user_id=user.id,
                    date=date,
                    planned_start=start,
                    planned_end=end,
                    actual_start=start,
                    actual_end=end,
                    latest_child_name=child,
                    latest_child_time=child_time,
                )
            )

        await db.commit()


asyncio.run(main())
