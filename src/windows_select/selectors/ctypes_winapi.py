import ctypes
import ctypes.wintypes as wintypes

ntdll = ctypes.windll.LoadLibrary("ntdll")


FilePipeInformation = ctypes.c_ulong(24)  # FILE_PIPE_LOCAL_INFORMATION

NtQueryInformationFile = ntdll.NtQueryInformationFile

# Define structures

if ctypes.sizeof(ctypes.c_void_p) == 8:
    ULONG_PTR = ctypes.c_ulonglong
else:
    ULONG_PTR = ctypes.c_ulong


class Info(ctypes.Union):
    """This is a Union for IoStatusBlock"""

    _fields_ = [
        ("Status", ctypes.c_long),
        ("Pointer", ctypes.c_void_p),
    ]


class io_stat(ctypes.Structure):
    """This is the IoStatusBlock"""

    _anonymous_ = ["status"]
    _fields_ = [
        ("status", Info),
        ("Information", ULONG_PTR),
    ]


class FILE_PIPE_LOCAL_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("NamedPipeType", ctypes.c_ulong),
        ("NamedPipeConfiguration", ctypes.c_ulong),
        ("MaximumInstances", ctypes.c_ulong),
        ("CurrentInstances", ctypes.c_ulong),
        ("InboundQuota", ctypes.c_ulong),
        ("ReadDataAvailable", ctypes.c_ulong),
        ("OutboundQuota", ctypes.c_ulong),
        ("WriteQuotaAvailable", ctypes.c_ulong),
        ("NamedPipeState", ctypes.c_ulong),
        ("NamedPipeEnd", ctypes.c_ulong),
    ]


# Set function argument and return types
NtQueryInformationFile.argtypes = [
    wintypes.HANDLE,  # FileHandle
    ctypes.POINTER(io_stat),  # IoStatusBlock
    ctypes.POINTER(FILE_PIPE_LOCAL_INFORMATION),  # FileInformation
    wintypes.ULONG,  # Length
    wintypes.ULONG,  # FileInformationClass
]
NtQueryInformationFile.restype = wintypes.LONG
