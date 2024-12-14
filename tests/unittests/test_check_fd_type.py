import os

import pytest

from windows_select.check_fd_type import (
    is_character_device,
    is_file,
    is_pipe,
    is_socket,
)


def test_is_pipe(pipe_fds):
    assert is_pipe(pipe_fds[0])
    assert is_pipe(pipe_fds[1])


def test_is_file(regular_file_fd):
    assert is_file(regular_file_fd)


def test_is_socket(socket_fd):
    assert is_socket(socket_fd)


def test_is_character_device(char_device_fd):
    assert is_character_device(char_device_fd)


@pytest.mark.parametrize("method", [is_pipe, is_file, is_character_device])
def test_socket_raises_exception(socket_fd, method):
    with pytest.raises(OSError):
        method(socket_fd)


@pytest.mark.parametrize("method", [is_socket, is_file, is_character_device])
def test_pipe_is_not_other_types(pipe_fds, method):
    assert not method(pipe_fds[0])
    assert not method(pipe_fds[1])


@pytest.mark.parametrize("method", [is_socket, is_pipe, is_character_device])
def test_regular_file_is_not_other_types(regular_file_fd, method):
    assert not method(regular_file_fd)


@pytest.mark.parametrize("method", [is_socket, is_file, is_pipe])
def test_char_device_is_not_other_types(char_device_fd, method):
    assert not method(char_device_fd)


def test_closed_fd(regular_file_fd, socket_fd):
    with pytest.raises(OSError):
        another_fd = os.dup(regular_file_fd)
        os.close(another_fd)
        assert is_file(another_fd)
    with pytest.raises(OSError):
        another_fd = os.dup(socket_fd)
        os.close(another_fd)
        assert is_socket(another_fd)
