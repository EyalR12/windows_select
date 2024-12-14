from concurrent.futures import ThreadPoolExecutor
from time import perf_counter_ns
from typing import Callable, List, Sequence

import win32file
from pywintypes import HANDLEType, error
from win32event import (
    WAIT_ABANDONED_0,
    WAIT_OBJECT_0,
    WAIT_TIMEOUT,
    CreateEvent,
    WaitForMultipleObjects,
)


def _select_events(handles: Sequence[HANDLEType], timeout=0) -> List[HANDLEType]:
    """Return ALL handles which are currently signalled.  (Only
    returning the first signalled might create starvation issues.)

    Args:
        handles (Sequence[HANDLEType]): A sequence of Windows Event Handles to wait on
        timeout (int): The timeout in milliseconds. Defaults to 0.

    Raises:
        RuntimeError: If the WINAPI WaitForMultipleObjects returned unexpected value

    Returns:
        List[HANDLEType]: all signaled Event handles
    """
    L = list(handles)
    ready = []
    while L:
        res = WaitForMultipleObjects(L, False, timeout)
        if res == WAIT_TIMEOUT:
            break
        elif WAIT_OBJECT_0 <= res < WAIT_OBJECT_0 + len(L):
            res -= WAIT_OBJECT_0
        elif WAIT_ABANDONED_0 <= res < WAIT_ABANDONED_0 + len(L):
            res -= WAIT_ABANDONED_0
        else:
            raise RuntimeError("Should not get here")
        ready.append(L[res])
        # WaitForMultipleObjects returns first handle that is signaled - we want to get all
        L = L[res + 1 :]
        # We already got an event - dont wait anymore
        timeout = 0
    return ready


def _select_template(
    handles: Sequence[HANDLEType],
    timeout,
    io_operation: Callable[[HANDLEType, win32file.OVERLAPPED], None],
) -> List[HANDLEType]:
    """Template for select operation

    Args:
        handles (Sequence[HANDLEType]): all handles to select on - must have read permission
        timeout (int, optional): like select - if no handle is signalled within timeout return nothing. Defaults to 0.
        io_operation (Callable[[HANDLEType, win32file.OVERLAPPED], None]): the io call depending - read or write

    Raises:
        OSError: if failed to perform io_operation on handle

    Returns:
        List[HANDLEType]: all ready handles
    """
    L = list(handles)
    event_to_handle = dict()
    for handle in L:
        overlapped = win32file.OVERLAPPED()
        overlapped.hEvent = CreateEvent(None, True, False, None)
        try:
            io_operation(handle, overlapped)
        except error as e:
            if e.winerror == 5:
                raise OSError(f"handle {handle} does not have read permissions!") from e
            raise
        event_to_handle[overlapped.hEvent] = handle
    signalled_events = _select_events(event_to_handle.keys(), timeout)
    ready_handles = [event_to_handle[event] for event in signalled_events]
    [event.close() for event in event_to_handle.keys()]
    return ready_handles


def read_select(rhandles: Sequence[HANDLEType], timeout=0) -> List[HANDLEType]:
    """Perform select on read handles

    Args:
        rhandles (Sequence[HANDLEType]): all handles to select on - must have read permission
        timeout (int, optional): like select - if no handle is signalled within timeout return nothing. Defaults to 0.

    Raises:
        OSError: if failed to perform read on handle

    Returns:
        List[HANDLEType]: all ready to read handles.
    """

    def io_operation(handle, overlapped):
        win32file.ReadFile(handle, 0, overlapped)

    start_time = perf_counter_ns()
    signalled = _select_template(rhandles, timeout, io_operation)
    end_time = perf_counter_ns()
    return _select_template(
        rhandles, max(0, timeout - (end_time - start_time)), io_operation
    )


def write_select(whandles: Sequence[HANDLEType], timeout=0) -> List[HANDLEType]:
    """Perform select on write handles

    Args:
        whandles (Sequence[HANDLEType]): all handles to select on - must have write permission
        timeout (int, optional): like select - if no handle is signalled within timeout return nothing. Defaults to 0.

    Raises:
        OSError: if failed to perform write on handle

    Returns:
        List[HANDLEType]: all ready to write handles.
    """

    def io_operation(handle, overlapped):
        win32file.WriteFile(handle, b"", overlapped)

    return _select_template(whandles, timeout, io_operation)


def select(
    rhandles: Sequence[HANDLEType], whandles: Sequence[HANDLEType], timeout=0
) -> tuple[List[HANDLEType], List[HANDLEType]]:
    """The combination of read_select and write_select - do not select on both ends of a pipe at the same time

    Args:
        rhandles (Sequence[HANDLEType]): handles to select on - must have read permission
        whandles (Sequence[HANDLEType]): handles to select on - must have write permission
        timeout (int, optional): like select - if no handle is signalled within timeout return nothing. Defaults to 0.

    Returns:
        tuple[List[HANDLEType], List[HANDLEType]]: a tuple of ready rhandles and ready whandles
    """
    with ThreadPoolExecutor() as rthread, ThreadPoolExecutor() as wthread:
        rfuture = rthread.submit(read_select, rhandles, timeout)
        wfuture = wthread.submit(write_select, whandles, timeout)
        read_ready = rfuture.result()
        write_ready = wfuture.result()
    return read_ready, write_ready
