from datetime import datetime, timedelta, timezone

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(
        String,
        unique=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String,
        default="",
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    starting_balance_minutes: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    sessions = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan",
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

    note: Mapped[str] = mapped_column(
        String,
        default="",
    )

    user = relationship("User")


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    token: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    created = datetime.now(timezone.utc)
    expires = created + timedelta(days=30)

    user = relationship(
        "User",
        back_populates="sessions",
    )
