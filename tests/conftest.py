import os
import socket
from tempfile import TemporaryFile

import pytest


@pytest.fixture(scope="function")
def pipe_fds():
    r, w = os.pipe()
    yield (r, w)
    os.close(r)
    os.close(w)


@pytest.fixture(scope="function")
def socket_fd():
    sock = socket.socket()
    yield sock.fileno()
    sock.close()


@pytest.fixture(scope="function")
def regular_file_fd():
    file = TemporaryFile("w")
    yield file.fileno()
    file.close()


@pytest.fixture(scope="function")
def char_device_fd():
    dev = open(os.devnull, "w")
    yield dev.fileno()
    dev.close()
