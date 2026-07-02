from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str


class ShiftBase(BaseModel):
    planned_start: str
    planned_end: str

    actual_start: str
    actual_end: str

    latest_child_name: str
    latest_child_time: str

    note: str = ""


class ShiftCreate(ShiftBase):
    date: str


class ShiftUpdate(ShiftBase):
    pass
