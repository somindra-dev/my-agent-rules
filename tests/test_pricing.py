import pytest

from app.pricing import apply_discount


def test_ten_percent_off():
    assert apply_discount(1000, 10) == 900


def test_bad_percent_is_refused():
    with pytest.raises(ValueError):
        apply_discount(1000, 150)
