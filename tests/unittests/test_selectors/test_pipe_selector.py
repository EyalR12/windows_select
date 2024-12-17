from queue import Queue
from threading import Event

import pytest

from windows_select.selectors.pipe_select import PipeSelector


@pytest.fixture
def shared_lists():
    return list(), list(), list()


@pytest.fixture(params=[True, False])
def with_write_end(request):
    return request.param


@pytest.fixture()
def inputs_to_select(pipe_fds, with_write_end):
    if with_write_end:
        return [pipe_fds[0]], [pipe_fds[1]], []
    return [pipe_fds[0]], [], []


@pytest.fixture
def pipe_selector(inputs_to_select):
    return PipeSelector(*inputs_to_select)


def test_pipe_selector(pipe_selector, with_write_end, shared_lists, select_timer):
    event = Event()
    if with_write_end:
        t = select_timer(2)
        t.start()
        pipe_selector.select(*shared_lists, event, Queue())
        t.cancel()
        assert shared_lists[1] and not shared_lists[0]
    else:
        t = select_timer(2)
        t.start()
        event.set()
        pipe_selector.select(*shared_lists, event, Queue())
        t.cancel()
        assert not shared_lists[1] and not shared_lists[0]
