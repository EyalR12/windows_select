import os
import socket
from tempfile import TemporaryFile

import pytest


@pytest.fixture(scope="function")
def pipe_fds():
    r, w = os.pipe()
    yield (r, w)
    for fd in (r, w):
        try:
            os.close(fd)
        except:
            pass  # Suppress exceptions for each `os.close`


@pytest.fixture(scope="function")
def socket_object():
    sock = socket.socket()
    yield sock
    try:
        sock.close()
    except:
        pass


@pytest.fixture(scope="function")
def regular_file_object():
    file = TemporaryFile("w")
    yield file
    try:
        file.close()
    except:
        pass


@pytest.fixture(scope="function")
def char_device_object():
    dev = open(os.devnull, "w")
    yield dev
    try:
        dev.close()
    except:
        pass
