import os

from windows_select.selectors.pipe_select import (
    get_pipe_info,
    pipe_read_available,
    pipe_write_available,
)


def test_no_data_to_read(pipe_fds):
    assert not pipe_read_available(pipe_fd=pipe_fds[0])


def test_data_to_read(pipe_fds):
    os.write(pipe_fds[1], b"example")
    assert pipe_read_available(pipe_fd=pipe_fds[0])


def test_empty_write_buffer(pipe_fds):
    assert pipe_write_available(pipe_fd=pipe_fds[1])


def test_full_write_buffer(pipe_fds):
    file_info = get_pipe_info(pipe_fds[1])
    os.write(pipe_fds[1], b"1" * file_info.OutboundQuota)
    assert not pipe_write_available(pipe_fd=pipe_fds[1])
