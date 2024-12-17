from typing import Callable, List, Optional, Tuple

from windows_select.check_fd_type import is_pipe
from windows_select.get_fd import get_fd
from windows_select.selectors.pipe_select import PipeSelector
from windows_select.selectors.select_manager import SelectManager


def extract_fds_by_type(fd_list: List[int], distinguisher_func: Callable[[int], bool]):
    pipe_fds = list()
    for fd in fd_list.copy():
        if distinguisher_func(get_fd(fd)):
            pipe_fds.append(fd)
            fd_list.remove(fd)
    return pipe_fds


def get_pipe_selector(rlist, wlist):
    pipe_rlist = extract_fds_by_type(rlist, is_pipe)
    pipe_wlist = extract_fds_by_type(wlist, is_pipe)
    if pipe_rlist or pipe_wlist:
        return PipeSelector(pipe_rlist, pipe_wlist, [])


def select(
    rlist: List[int],
    wlist: List[int],
    xlist: List[int],
    timeout: Optional[float] = None,
) -> Tuple[List[int], List[int], List[int]]:
    select_manager = SelectManager([], timeout=timeout)
    if pipe_selector := get_pipe_selector(rlist, wlist):
        select_manager.add_selectors(pipe_selector)
    return select_manager.select_all()
