import os

from windows_select import select


def test_pipe_select(pipe_fds):
    r, w = pipe_fds
    assert select([r], [w], [], 5) == ([], [w], [])
    os.write(w, b"123")
    assert select([r], [w], []) == ([r], [w], [])


def test_file_select(regular_file_fd):
    assert select([regular_file_fd], [regular_file_fd], [], 5) == (
        [regular_file_fd],
        [regular_file_fd],
        [],
    )
