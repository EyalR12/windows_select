import win32file
from pywintypes import HANDLEType, error
from win32event import CreateEvent, ResetEvent
from winerror import ERROR_HANDLE_EOF, ERROR_IO_PENDING

from windows_select.select import _select_events

BUFFER_SIZE = 8 * 1024


class SelectableObject:
    def __init__(self, handle: HANDLEType, readable=False, writeable=False):
        """An IO object that can be used with this package's select method.

        Args:
            handle (HANDLEType): handle of IO object
            readable (bool, optional): if the object is readable. Defaults to False.
            writeable (bool, optional): if the object is writeable. Defaults to False.
        """
        self._handle = handle
        self._readable = readable
        self._writeable = writeable
        self._overlapped = win32file.OVERLAPPED()
        self._overlapped.hEvent = CreateEvent(None, True, False, None)

    def read(self, size: int) -> bytes:
        """read data

        Args:
            size (int): the number of bytes to read

        Returns:
            bytes: the data
        """
        if not isinstance(size, int):
            raise TypeError("size must be an int")
        if size < 0:
            raise ValueError("size must be a positive int")
        size = min(size, BUFFER_SIZE)

        assert self.readable, "The Object does not have read permission!"

        err, data_buffer = win32file.ReadFile(self._handle, size, self._overlapped)
        if err == ERROR_IO_PENDING:
            res = _select_events([self._overlapped.hEvent], 0xFFFFFFFF)
            assert res

        try:
            self.update_ovelapped_offset(
                win32file.GetOverlappedResult(self.fileno(), self._overlapped, True)
            )
        except error as e:
            if e.winerror == ERROR_HANDLE_EOF:
                self._overlapped.InternalHigh = 0
            else:
                raise

        ResetEvent(self._overlapped.hEvent)
        return bytes(data_buffer[: self._overlapped.InternalHigh])

    def write(self, data: bytes) -> int:
        """write data

        Args:
            data (bytes): data to write

        Returns:
            int: how much was written
        """
        if not isinstance(data, bytes):
            raise TypeError("data must be a bytes object")

        assert self.writeable, "The Object does not have write permission!"

        err, bytes_sent = win32file.WriteFile(self._handle, data, self._overlapped)

        if err == ERROR_IO_PENDING:
            res = _select_events([self._overlapped.hEvent], 0xFFFFFFFF)
            assert res
            bytes_sent = win32file.GetOverlappedResult(
                self.fileno(), self._overlapped, True
            )

        self.update_ovelapped_offset(bytes_sent)
        ResetEvent(self._overlapped.hEvent)
        return bytes_sent

    def update_ovelapped_offset(self, additional_offset):
        current_offset = (self._overlapped.OffsetHigh << 32) + self._overlapped.Offset
        new_offset = current_offset + additional_offset
        self._overlapped.Offset = new_offset % (1 << 32)
        self._overlapped.OffsetHigh = new_offset >> 32

    def fileno(self) -> HANDLEType:
        return self._handle

    @property
    def readable(self) -> bool:
        return self._readable

    @property
    def writeable(self) -> bool:
        return self._writeable

    def close(self):
        self._handle.close()

    def __del__(self):
        self.close()
