import pytest
from fastapi import HTTPException

from app.validators import (
    validate_shift_data,
    validate_time,
)


def test_validate_time_ok():
    assert validate_time("08:00")


def test_validate_time_bad():
    assert not validate_time("25:00")


def test_validate_shift_data_ok():
    validate_shift_data(
        "08:00",
        "16:00",
        "08:00",
        "16:30",
        "15:45",
    )


def test_validate_shift_data_bad_end():
    with pytest.raises(HTTPException):
        validate_shift_data(
            "16:00",
            "08:00",
            "08:00",
            "16:00",
            "15:45",
        )
