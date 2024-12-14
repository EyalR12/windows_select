import os
import socket

# This is nice results for os.fstat.st_mode to check the type of object

# define _S_IFMT   0xF000 // File type mask
# define _S_IFDIR  0x4000 // Directory
# define _S_IFCHR  0x2000 // Character special
# define _S_IFIFO  0x1000 // Pipe
# define _S_IFREG  0x8000 // Regular
# define _S_IREAD  0x0100 // Read permission, owner
# define _S_IWRITE 0x0080 // Write permission, owner
# define _S_IEXEC  0x0040 // Execute/search permission, owner

MASK_VALUE = 0xF000
REGULAR_FILE_VALUE = 0x8000
PIPE_VALUE = 0x1000
CHAR_DEVICE = 0x2000


def is_socket(fd):
    try:
        s = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
        s.close()
        return True
    except OSError:
        return False


def check_file_type(fd, desired_file_type):
    # We assume here that we dont get socket fds - as we are supposed to
    # identify them earlier on with `is_socket` function.
    stat = os.fstat(fd)
    return stat.st_mode & MASK_VALUE == desired_file_type


def is_pipe(fd):
    return check_file_type(fd, PIPE_VALUE)


def is_file(fd):
    return check_file_type(fd, REGULAR_FILE_VALUE)


def is_character_device(fd):
    return check_file_type(fd, CHAR_DEVICE)
