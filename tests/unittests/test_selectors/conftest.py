from threading import Timer

import pytest

from windows_select.selectors.select_manager import SelectManager


@pytest.fixture
def select_manager():
    return SelectManager([])


@pytest.fixture
def select_timer():
    def timeout_func():
        raise TimeoutError("select_manager didn't return")

    def timer(interval):
        return Timer(interval, timeout_func)

    return timer
