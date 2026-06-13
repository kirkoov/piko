from app.timecalc import (
    duration,
    evening_bonus,
    morning_bonus,
    recommended_shift,
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


def test_morning_bonus():
    assert morning_bonus("05:00", "06:00") == 18


def test_evening_bonus():
    assert evening_bonus("18:00", "19:00") == 8


def test_recommended_shift():
    assert (
        recommended_shift(
            "08:00",
            "16:00",
            "15:00",
        )
        == "07:00-15:00"
    )

def test_recommended_shift_none_child_leaves_later():
    assert (
        recommended_shift(
            "08:00",
            "16:00",
            "16:30",
        )
        is None
    )

def test_recommended_shift_none_child_leaves_same_time():
    assert (
        recommended_shift(
            "08:00",
            "16:00",
            "16:00",
        )
        is None
    )

def test_recommended_shift_one_minute_before_end():
    assert (
        recommended_shift(
            "08:00",
            "16:00",
            "15:59",
        )
        == "07:59-15:59"
    )