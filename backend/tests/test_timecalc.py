from app.timecalc import (
    duration,
    evening_bonus,
    morning_bonus,
    overlap_minutes,
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


def test_morning_bonus_partial_block():
    assert morning_bonus("05:00", "05:29") == 0


def test_morning_bonus_exact_block():
    assert morning_bonus("05:00", "05:30") == 9


def test_evening_bonus_partial_block():
    assert evening_bonus("18:00", "18:29") == 0


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


def test_recommended_shift_preserves_duration():
    result = recommended_shift(
        "08:00",
        "16:00",
        "15:00",
    )
    assert result is not None
    start, end = result.split("-")
    assert duration(start, end) == duration("08:00", "16:00")


def test_overlap_no_overlap():
    assert (
        overlap_minutes(
            "08:00",
            "09:00",
            "18:00",
            "22:00",
        )
        == 0
    )


def test_overlap_partial():
    assert (
        overlap_minutes(
            "17:30",
            "18:30",
            "18:00",
            "22:00",
        )
        == 30
    )
