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
def socket_object():
    sock = socket.socket()
    yield sock
    sock.close()


@pytest.fixture(scope="function")
def regular_file_object():
    file = TemporaryFile("w")
    yield file
    file.close()


@pytest.fixture(scope="function")
def char_device_object():
    dev = open(os.devnull, "w")
    yield dev
    dev.close()
