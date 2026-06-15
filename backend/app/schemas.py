from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str


class ShiftCreate(BaseModel):
    user_id: int

    date: str

    planned_start: str
    planned_end: str

    actual_start: str
    actual_end: str

    latest_child_name: str
    latest_child_time: str

    note: str = ""
