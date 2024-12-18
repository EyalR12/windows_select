import select

from windows_select.selectors.base_select_object import BaseSelector


class SocketSelector(BaseSelector):
    def __init__(self, rlist, wlist, xlist):
        super().__init__(rlist, wlist, xlist)

    def select(self, result_rlist, result_wlist, result_xlist, event, queue):
        should_continue = True
        try:
            while should_continue:
                if any(
                    res := select.select(
                        self.rlist, self.wlist, self.xlist, self.EVENT_WAIT
                    )
                ):
                    event.set()
                    result_rlist.extend(res[0])
                    result_wlist.extend(res[1])
                    result_xlist.extend(res[2])

                should_continue = not event.wait(self.EVENT_WAIT)
        except BaseException as e:
            event.set()
            queue.put(e)
