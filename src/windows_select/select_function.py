from typing import Callable, List, Optional, Tuple

from windows_select.check_fd_type import is_file, is_pipe, is_socket
from windows_select.get_fd import get_fd
from windows_select.selectors.file_select import FileSelector
from windows_select.selectors.pipe_select import PipeSelector
from windows_select.selectors.select_manager import SelectManager
from windows_select.selectors.socket_select import SocketSelector


def extract_fds_by_type(fd_list: List[int], distinguisher_func: Callable[[int], bool]):
    fds = list()
    for fd in fd_list.copy():
        if distinguisher_func(get_fd(fd)):
            fds.append(fd)
            fd_list.remove(fd)
    return fds


def get_pipe_selector(rlist, wlist, xlist):
    pipe_rlist = extract_fds_by_type(rlist, is_pipe)
    pipe_wlist = extract_fds_by_type(wlist, is_pipe)
    pipe_xlist = extract_fds_by_type(xlist, is_pipe)
    if any((pipe_rlist, pipe_wlist, pipe_xlist)):
        return PipeSelector(pipe_rlist, pipe_wlist, pipe_xlist)


def get_file_selector(rlist, wlist, xlist):
    file_rlist = extract_fds_by_type(rlist, is_file)
    file_wlist = extract_fds_by_type(wlist, is_file)
    file_xlist = extract_fds_by_type(xlist, is_file)
    if any((file_rlist, file_wlist, file_xlist)):
        return FileSelector(file_rlist, file_wlist, file_xlist)


def get_socket_selector(rlist, wlist, xlist):
    socket_rlist = extract_fds_by_type(rlist, is_socket)
    socket_wlist = extract_fds_by_type(wlist, is_socket)
    socket_xlist = extract_fds_by_type(xlist, is_socket)
    if any((socket_rlist, socket_wlist, socket_xlist)):
        return SocketSelector(socket_rlist, socket_wlist, socket_xlist)


def select(
    rlist: List[int],
    wlist: List[int],
    xlist: List[int],
    timeout: Optional[float] = None,
) -> Tuple[List[int], List[int], List[int]]:
    select_manager = SelectManager([], timeout=timeout)

    available_selectors = [get_socket_selector, get_pipe_selector, get_file_selector]

    for available_selector in available_selectors:
        if selector := available_selector(rlist, wlist, xlist):
            select_manager.add_selector(selector)

    if any((rlist, wlist, xlist)):
        raise OSError(f"Got unsupported objects: {rlist + wlist + xlist}")

    return select_manager.select_all()
