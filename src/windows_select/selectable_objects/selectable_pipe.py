from itertools import count
from os import getpid

import win32file
import win32pipe

from windows_select.selectable_objects.selectable_object import (
    BUFFER_SIZE,
    SelectableObject,
)

pipes_counter = count()


def pipe() -> tuple[SelectableObject, SelectableObject]:
    pipe_address = rf"\\.\pipe\selectable-pipe-{getpid()}-{next(pipes_counter)}-"
    reader = win32pipe.CreateNamedPipe(
        pipe_address,
        win32pipe.PIPE_ACCESS_INBOUND
        | win32pipe.FILE_FLAG_FIRST_PIPE_INSTANCE
        | win32file.FILE_FLAG_OVERLAPPED,
        win32pipe.PIPE_TYPE_MESSAGE
        | win32pipe.PIPE_READMODE_MESSAGE
        | win32pipe.PIPE_WAIT,
        1,
        0,
        BUFFER_SIZE,
        win32pipe.NMPWAIT_WAIT_FOREVER,
        None,
    )
    writer = win32file.CreateFile(
        pipe_address,
        win32file.GENERIC_WRITE,
        0,
        None,
        win32file.OPEN_EXISTING,
        win32file.FILE_FLAG_OVERLAPPED,
        None,
    )
    win32pipe.SetNamedPipeHandleState(
        writer, win32pipe.PIPE_READMODE_MESSAGE, None, None
    )
    over = win32file.OVERLAPPED()
    win32pipe.ConnectNamedPipe(reader, over)
    assert (
        win32file.GetOverlappedResult(writer, over, True) == 0
    ), "Failed to connect Pipe"

    return SelectableObject(reader, readable=True), SelectableObject(
        writer, writeable=True
    )
