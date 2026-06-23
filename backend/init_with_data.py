import asyncio

from app.auth import hash_password
from app.database import SessionLocal
from app.models import Shift, User


async def main():
    async with SessionLocal() as db:
        kk = User(
            name="kk",
            password_hash=hash_password("test123"),
            is_admin=True,
        )

        lora = User(
            name="Lora",
            password_hash=hash_password("change_me"),
            starting_balance_minutes=36,
        )

        masha = User(
            name="Masha",
            password_hash=hash_password("change_me"),
        )

        db.add_all([kk, lora, masha])
        await db.flush()

        shifts = [
            (
                "2026-06-08",
                "13:30",
                "21:30",
                "13:30",
                "21:30",
                "Masha",
                "21:15",
                "",
            ),
            # Child leaves early, Lora leaves too
            (
                "2026-06-09",
                "14:30",
                "22:30",
                "14:30",
                "21:45",
                "Petya",
                "21:45",
                "Left with latest child",
            ),
            (
                "2026-06-10",
                "14:15",
                "21:30",
                "14:15",
                "21:30",
                "Vanya",
                "21:00",
                "",
            ),
            # SMS before shift -> shift moved earlier
            (
                "2026-06-11",
                "13:00",
                "21:00",
                "13:00",
                "21:00",
                "Sofia",
                "21:00",
                "Shift adjusted before start",
            ),
            (
                "2026-06-12",
                "14:30",
                "21:30",
                "14:30",
                "21:30",
                "Artem",
                "21:00",
                "",
            ),
            (
                "2026-06-29",
                "14:30",
                "21:30",
                "14:30",
                "21:30",
                "Artem",
                "21:30",
                "",
            ),
            (
                "2026-06-30",
                "14:30",
                "21:30",
                "14:30",
                "21:30",
                "Artem",
                "21:30",
                "",
            ),
            (
                "2026-07-01",
                "14:30",
                "21:30",
                "14:30",
                "21:30",
                "Artem",
                "21:30",
                "",
            ),
            (
                "2026-07-02",
                "14:30",
                "21:30",
                "14:30",
                "21:30",
                "Artem",
                "21:30",
                "",
            ),
        ]

        for (
            date,
            p_start,
            p_end,
            a_start,
            a_end,
            child,
            child_time,
            note,
        ) in shifts:
            db.add(
                Shift(
                    user_id=lora.id,
                    date=date,
                    planned_start=p_start,
                    planned_end=p_end,
                    actual_start=a_start,
                    actual_end=a_end,
                    latest_child_name=child,
                    latest_child_time=child_time,
                    note=note,
                )
            )

        await db.commit()


asyncio.run(main())
