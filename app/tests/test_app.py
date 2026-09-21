import pytest
from app import add, subtract, multiply, divide, save_calculation, get_history


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0


def test_subtract():
    assert subtract(10, 3) == 7


def test_multiply():
    assert multiply(4, 5) == 20


def test_divide():
    assert divide(10, 2) == 5.0


def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)


def test_save_and_retrieve_calculation():
    save_calculation("add", 2, 3, 5)
    history = get_history()
    assert len(history) > 0
    latest = history[0]
    assert latest[0] == "add"
    assert latest[1] == 2.0
    assert latest[2] == 3.0
    assert latest[3] == 5.0


def test_history_returns_last_10():
    for i in range(12):
        save_calculation("multiply", i, 2, i * 2)
    history = get_history()
    assert len(history) == 10
