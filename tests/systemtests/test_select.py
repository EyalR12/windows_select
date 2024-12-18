import os
import socket

import pytest

from windows_select import select

SERVER_ADDR = ("loopback", 12345)


@pytest.fixture
def server_sock():
    server_sock = socket.socket()
    server_sock.bind(SERVER_ADDR)
    server_sock.listen(1)
    yield server_sock
    server_sock.close()


def test_pipe_select(pipe_fds):
    r, w = pipe_fds
    assert select([r], [w], [], 2) == ([], [w], [])
    os.write(w, b"123")
    assert select([r], [w], []) == ([r], [w], [])


def test_file_select(regular_file_object):
    assert select([regular_file_object], [regular_file_object], [], 5) == (
        [regular_file_object],
        [regular_file_object],
        [],
    )


def test_socket_select(socket_object, server_sock):
    assert select([socket_object], [], [], 2) == ([], [], [])
    socket_object.connect(SERVER_ADDR)
    connected_sock = server_sock.accept()[0]
    connected_sock.send(b"12")
    assert select([socket_object], [], [], 2) == ([socket_object], [], [])
    connected_sock.close()


def test_closed_fds(pipe_fds):
    r, w = pipe_fds
    os.close(r)
    with pytest.raises(OSError):
        select([r], [], [])


def test_select(socket_object, regular_file_object, pipe_fds):
    os.write(pipe_fds[1], b"1")
    expected_res = ({pipe_fds[0]}, {regular_file_object, pipe_fds[1]}, set())
    rlist, wlist, xlist = select(
        [socket_object, pipe_fds[0]],
        [regular_file_object, pipe_fds[1]],
        [socket_object],
    )
    assert (set(rlist), set(wlist), set(xlist)) == expected_res
