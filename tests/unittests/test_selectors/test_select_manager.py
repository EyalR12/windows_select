from unittest.mock import MagicMock

import pytest

from windows_select.selectors.base_select_object import BaseSelector




@pytest.fixture
def mock_selector():
    return MagicMock(BaseSelector)


def test_no_selectors(select_manager):
    assert select_manager.select_all() == ([], [], [])


def test_timeout(select_manager, mock_selector, select_timer):
    select_manager.timeout = 2
    select_manager.add_selectors(mock_selector)
    t = select_timer(select_manager.timeout + 1)
    t.start()
    select_manager.select_all()
    t.cancel()
