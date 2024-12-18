import os

import pytest

from windows_select.check_fd_type import (
    is_character_device,
    is_file,
    is_pipe,
    is_socket,
)
from windows_select.get_fd import get_fd


def test_is_pipe(pipe_fds):
    assert is_pipe(pipe_fds[0])
    assert is_pipe(pipe_fds[1])


def test_is_file(regular_file_object):
    assert is_file(get_fd(regular_file_object))


def test_is_socket(socket_object):
    assert is_socket(get_fd(socket_object))


def test_is_character_device(char_device_object):
    assert is_character_device(get_fd(char_device_object))


@pytest.mark.parametrize("method", [is_pipe, is_file, is_character_device])
def test_socket_is_not_other_types(socket_object, method):
    assert not method(get_fd(socket_object))


@pytest.mark.parametrize("method", [is_socket, is_file, is_character_device])
def test_pipe_is_not_other_types(pipe_fds, method):
    assert not method(get_fd(pipe_fds[0]))
    assert not method(get_fd(pipe_fds[1]))


@pytest.mark.parametrize("method", [is_socket, is_pipe, is_character_device])
def test_regular_file_is_not_other_types(regular_file_object, method):
    assert not method(get_fd(regular_file_object))


@pytest.mark.parametrize("method", [is_socket, is_file, is_pipe])
def test_char_device_is_not_other_types(char_device_object, method):
    assert not method(get_fd(char_device_object))


@pytest.mark.parametrize("method", [is_file, is_pipe, is_character_device])
def test_closed_fd(regular_file_object, method):
    with pytest.raises(OSError):
        another_fd = os.dup(get_fd(regular_file_object))
        os.close(another_fd)
        assert not method(another_fd)
