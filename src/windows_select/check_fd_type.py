import os
import socket

MASK_VALUE = 0xF000
REGULAR_FILE_VALUE = 0x8000
PIPE_VALUE = 0x1000
CHAR_DEVICE = 0x2000


def is_socket(fd: int) -> bool:
    """Checks if an fd is representing a socket

    Args:
        fd (int): an int representing an fd

    Returns:
        bool: True if fd corresponds to socket.
    """
    try:
        s = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
        s.close()
        return True
    except OSError:
        return False


def check_file_type_template(fd: int, file_type_mask: int) -> bool:
    """A template function to check if an fd correspond to some file type using os.fstat.

    Args:
        fd (int): an int representing an fd
        file_type_mask (int): a mask for the file type.

    Raises:
        OSError: if fd is not valid or fd belongs to socket.

    Returns:
        bool: True if fd correspond to the file_type_mask.
    """
    if is_socket(fd):
        return False
    stat = os.fstat(fd)
    return stat.st_mode & MASK_VALUE == file_type_mask


def is_pipe(fd: int) -> bool:
    """Checks if an fd represents a pipe object

    Args:
        fd (int): an int representing an fd

    Returns:
        bool: True if fd represents a pipe
    """
    return check_file_type_template(fd, PIPE_VALUE)


def is_file(fd: int) -> bool:
    """Checks if an fd represents a regular file object

    Args:
        fd (int): an int representing an fd

    Returns:
        bool: True if fd represents a regular file
    """
    return check_file_type_template(fd, REGULAR_FILE_VALUE)


def is_character_device(fd: int) -> bool:
    """Checks if an fd represents a character device object

    Args:
        fd (int): an int representing an fd

    Returns:
        bool: True if fd represents a character device
    """
    return check_file_type_template(fd, CHAR_DEVICE)
