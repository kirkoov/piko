import asyncio
from datetime import date as d
from datetime import timedelta

from app.auth import hash_password
from app.database import SessionLocal
from app.models import Shift, User
from app.period import period_for_date


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

        today = d.today()

        period_start_str, _ = period_for_date(today.isoformat())
        period_start = d.fromisoformat(period_start_str)

        shifts = [
            (
                (period_start + timedelta(days=0)).isoformat(),
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
                (period_start + timedelta(days=1)).isoformat(),
                "14:30",
                "22:30",
                "14:30",
                "21:45",
                "Petya",
                "21:45",
                "Left with latest child",
            ),
            (
                (period_start + timedelta(days=2)).isoformat(),
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
                (period_start + timedelta(days=3)).isoformat(),
                "13:00",
                "21:00",
                "13:00",
                "21:00",
                "Sofia",
                "21:00",
                "Shift adjusted before start",
            ),
            (
                (period_start + timedelta(days=4)).isoformat(),
                "14:30",
                "21:30",
                "14:30",
                "21:30",
                "Artem",
                "21:00",
                "",
            ),
            (
                (period_start + timedelta(days=21)).isoformat(),
                "14:30",
                "21:30",
                "14:30",
                "21:30",
                "Artem",
                "21:30",
                "",
            ),
            (
                (period_start + timedelta(days=22)).isoformat(),
                "14:30",
                "21:30",
                "14:30",
                "21:30",
                "Artem",
                "21:30",
                "",
            ),
            (
                (period_start + timedelta(days=23)).isoformat(),
                "14:30",
                "21:30",
                "14:30",
                "21:30",
                "Artem",
                "21:30",
                "",
            ),
            (
                (period_start + timedelta(days=24)).isoformat(),
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
            shift_date,
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
                    date=shift_date,
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


if __name__ == "__main__":
    asyncio.run(main())
