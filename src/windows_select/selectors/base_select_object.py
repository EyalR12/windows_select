from abc import ABC, abstractmethod
from queue import Queue
from threading import Event
from typing import List


class BaseSelector(ABC):
    EVENT_WAIT = 0.1

    def __init__(self, rlist: List[int], wlist: List[int], xlist: List[int]):
        super().__init__()
        self.rlist = rlist
        self.wlist = wlist
        self.xlist = xlist

    @abstractmethod
    def select(
        self,
        result_rlist: List[int],
        result_wlist: List[int],
        result_xlist: List[int],
        event: Event,
        queue: Queue,
    ): ...
