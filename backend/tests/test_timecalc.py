from app.timecalc import (
    duration,
    shift_difference,
    to_minutes,
)


def test_to_minutes():
    assert to_minutes("08:00") == 480
    assert to_minutes("16:30") == 990


def test_duration():
    assert duration("08:00", "16:00") == 480


def test_shift_difference_positive():
    assert (
        shift_difference(
            "08:00",
            "16:00",
            "08:00",
            "17:00",
        )
        == 60
    )


def test_shift_difference_negative():
    assert (
        shift_difference(
            "08:00",
            "16:00",
            "08:00",
            "15:30",
        )
        == -30
    )
