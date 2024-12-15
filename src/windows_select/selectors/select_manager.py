from queue import Queue
from threading import Event, Lock, Thread
from typing import List, Tuple


def synchronized_method(lock):
    def decorator(method):
        def wrapper(*args, **kwargs):
            with lock:
                return method(*args, **kwargs)

        return wrapper

    return decorator


class SafeSharedList(list):
    def __init__(self):
        """A wrapper for list with Lock synchronization"""
        super().__init__()
        self.lock = Lock()

        # wrap all methods in lock call.
        for attr_name in dir(self):
            if callable(getattr(self, attr_name)) and not attr_name.startswith("_"):
                setattr(
                    self,
                    attr_name,
                    synchronized_method(self.lock)(getattr(self, attr_name)),
                )


class SelectManager:
    def __init__(self, selector_objects, timeout=0.0):
        self.selector_objects = selector_objects
        self.selector_threads: List[Thread] = list()
        self.read_ready = SafeSharedList()
        self.write_ready = SafeSharedList()
        self.except_ready = SafeSharedList()
        self.event = Event()
        self.queue = Queue()
        self.timeout = timeout

    def dispatch_selectors(self):
        for selector_object in self.selector_objects:
            t = Thread(
                target=selector_object.select,
                args=(
                    self.read_ready,
                    self.write_ready,
                    self.except_ready,
                    self.event,
                    self.queue,
                ),
            )
            t.start()
            self.selector_threads.append(t)

    def finalize_results(self) -> bool:
        self.event.wait(self.timeout)
        # whether we got True or False is irrelevant since
        # we want all threads to end - so we can skip if conditions
        self.event.set()
        for selector in self.selector_threads:
            selector.join()

    def select_all(self) -> Tuple[List[int], List[int], List[int]]:
        """preform the select itself

        Returns:
            Tuple[List[int], List[int], List[int]]: like the result of select
        """
        self.dispatch_selectors()
        self.finalize_results()
        res = self.read_ready.copy(), self.write_ready.copy(), self.except_ready.copy()
        self.clear_lists()
        if exc_count := self.queue.qsize():
            raise self.queue.get()

        return res

    def clear_lists(self):
        self.read_ready.clear()
        self.write_ready.clear()
        self.except_ready.clear()
