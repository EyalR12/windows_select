from contextlib import contextmanager
from typing import Generator

import win32file

from windows_select.selectable_objects.selectable_object import (
    BUFFER_SIZE,
    SelectableObject,
)


def open_file(file_path: str, mode="rb") -> SelectableObject:
    assert mode in ["rb", "wb", "wb+", "rb+"], "Only supports binary operation"
    if "+" in mode:
        access_mode = win32file.GENERIC_READ | win32file.GENERIC_WRITE
        disposition = win32file.OPEN_ALWAYS
    elif "r" in mode:
        access_mode = win32file.GENERIC_READ
        disposition = win32file.OPEN_EXISTING
    else:
        access_mode = win32file.GENERIC_WRITE
        disposition = win32file.OPEN_ALWAYS

    handle = win32file.CreateFile(
        file_path,
        access_mode,
        win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
        None,
        disposition,
        win32file.FILE_FLAG_OVERLAPPED,
        None,
    )
    f = SelectableObject(
        handle,
        readable=access_mode & win32file.GENERIC_READ,
        writeable=access_mode & win32file.GENERIC_WRITE,
    )
    return f


@contextmanager
def open_and_close(
    file_path: str, mode="rb"
) -> Generator[SelectableObject, None, None]:
    f = open_file(file_path, mode)
    yield f
    f.close()
