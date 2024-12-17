from windows_select.selectors.base_select_object import BaseSelector


class FileSelector(BaseSelector):
    def __init__(self, rlist, wlist, xlist):
        super().__init__(rlist, wlist, xlist)

    def select(self, result_rlist, result_wlist, result_xlist, event, queue):
        # Regular disk files are always ready
        if self.rlist:
            result_rlist.extend(self.rlist)
            event.set()

        if self.wlist:
            result_wlist.extend(self.wlist)
            event.set()
