import ctypes
from msvcrt import get_osfhandle
from typing import List

from windows_select.selectors.base_select_object import BaseSelector
from windows_select.selectors.ctypes_use import (
    FILE_PIPE_LOCAL_INFORMATION,
    FilePipeInformation,
    NtQueryInformationFile,
    io_stat,
)


def get_pipe_info(pipe_fd: int) -> FILE_PIPE_LOCAL_INFORMATION:
    """Query pipe metadata using NtQueryInformationFile api call

    Args:
        pipe_fd (int): an fd of a pipe

    Raises:
        OSError: in case call to NtQueryInformationFile failed

    Returns:
        FILE_PIPE_LOCAL_INFORMATION: a struct containing useful metadata on the pipe - refer to msdn for details
    """
    stat = io_stat()
    file_info = FILE_PIPE_LOCAL_INFORMATION()

    res = NtQueryInformationFile(
        get_osfhandle(pipe_fd),
        ctypes.byref(stat),
        ctypes.byref(file_info),
        ctypes.sizeof(file_info),
        FilePipeInformation,
    )
    if res != 0:
        raise OSError(f"NTSTATUS code is {res}")
    return file_info


def pipe_read_available(pipe_fd: int) -> bool:
    """Check if there if the pipe's read buffer is not empty

    Args:
        pipe_fd (int): an fd of a pipe

    Returns:
        bool: True if there is data to read
    """
    file_info = get_pipe_info(pipe_fd)

    return file_info.ReadDataAvailable > 0


def pipe_write_available(pipe_fd: int) -> bool:
    """Check if there if the pipe's write buffer is not full

    Args:
        pipe_fd (int): an fd of a pipe

    Returns:
        bool: True if buffer is not full
    """
    file_info = get_pipe_info(pipe_fd)

    return file_info.WriteQuotaAvailable > 0


class PipeSelector(BaseSelector):
    def __init__(self, rlist, wlist, xlist):
        super().__init__(rlist, wlist, xlist)

    def select(self, result_rlist, result_wlist, result_xlist, event):
        should_continue = True
        try:
            while should_continue:
                for rfd in self.rlist:
                    if pipe_read_available(rfd):
                        result_rlist.append(rfd)
                        event.set()

                for wfd in self.wlist:
                    if pipe_write_available(wfd):
                        result_wlist.append(wfd)
                        event.set()

                should_continue = not event.wait(self.EVENT_WAIT)
        except:
            event.set()
            raise
