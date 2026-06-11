from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)

    starting_balance_minutes: Mapped[int] = mapped_column(
        Integer,
        default=56,  # in minutes!
    )


class Shift(Base):
    __tablename__ = "shifts"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_user_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    date: Mapped[str] = mapped_column(String)

    planned_start: Mapped[str] = mapped_column(String)
    planned_end: Mapped[str] = mapped_column(String)

    actual_start: Mapped[str] = mapped_column(String)
    actual_end: Mapped[str] = mapped_column(String)

    latest_child_name: Mapped[str] = mapped_column(String)
    latest_child_time: Mapped[str] = mapped_column(String)

    user = relationship("User")
