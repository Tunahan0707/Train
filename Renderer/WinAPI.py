
import ctypes

# Windows sabitleri
WM_DESTROY = 0x0002
WM_QUIT = 0x0012

WS_OVERLAPPED = 0x00000000
WS_CAPTION = 0x00C00000
WS_SYSMENU = 0x00080000
WS_THICKFRAME = 0x00040000
WS_MINIMIZEBOX = 0x00020000
WS_MAXIMIZEBOX = 0x00010000

WS_OVERLAPPEDWINDOW = (
    WS_OVERLAPPED |
    WS_CAPTION |
    WS_SYSMENU |
    WS_THICKFRAME |
    WS_MINIMIZEBOX |
    WS_MAXIMIZEBOX
)

SW_SHOW = 1

# DLL
user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

# Callback türü
WNDPROC = ctypes.WINFUNCTYPE(
    ctypes.c_ssize_t,
    ctypes.c_void_p,
    ctypes.c_uint,
    ctypes.c_size_t,
    ctypes.c_ssize_t
)

# Yapılar
class POINT(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_long),
        ("y", ctypes.c_long)
    ]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", ctypes.c_void_p),
        ("message", ctypes.c_uint),
        ("wParam", ctypes.c_size_t),
        ("lParam", ctypes.c_ssize_t),
        ("time", ctypes.c_uint),
        ("pt", POINT)
    ]


class WNDClass(ctypes.Structure):
    _fields_ = [
        ("style", ctypes.c_uint),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", ctypes.c_void_p),
        ("hIcon", ctypes.c_void_p),
        ("hCursor", ctypes.c_void_p),
        ("hbrBackground", ctypes.c_void_p),
        ("lpszMenuName", ctypes.c_wchar_p),
        ("lpszClassName", ctypes.c_wchar_p)
    ]


# API fonksiyonları
DefWindowProcW = user32.DefWindowProcW
DefWindowProcW.argtypes = [
    ctypes.c_void_p,
    ctypes.c_uint,
    ctypes.c_size_t,
    ctypes.c_ssize_t
]
DefWindowProcW.restype = ctypes.c_ssize_t

PostQuitMessage = user32.PostQuitMessage
PostQuitMessage.argtypes = [ctypes.c_int]
PostQuitMessage.restype = None

GetModuleHandleW = kernel32.GetModuleHandleW
GetModuleHandleW.argtypes = [ctypes.c_wchar_p]
GetModuleHandleW.restype = ctypes.c_void_p

RegisterClassW = user32.RegisterClassW
RegisterClassW.argtypes = [ctypes.POINTER(WNDClass)]
RegisterClassW.restype = ctypes.c_ushort

CreateWindowExW = user32.CreateWindowExW
CreateWindowExW.argtypes = [
    ctypes.c_uint,
    ctypes.c_wchar_p,
    ctypes.c_wchar_p,
    ctypes.c_uint,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p
]
CreateWindowExW.restype = ctypes.c_void_p

ShowWindow = user32.ShowWindow
ShowWindow.argtypes = [ctypes.c_void_p, ctypes.c_int]
ShowWindow.restype = ctypes.c_int

GetMessageW = user32.GetMessageW
GetMessageW.argtypes = [
    ctypes.POINTER(MSG),
    ctypes.c_void_p,
    ctypes.c_uint,
    ctypes.c_uint
]
GetMessageW.restype = ctypes.c_int

TranslateMessage = user32.TranslateMessage
TranslateMessage.argtypes = [ctypes.POINTER(MSG)]
TranslateMessage.restype = ctypes.c_int

DispatchMessageW = user32.DispatchMessageW
DispatchMessageW.argtypes = [ctypes.POINTER(MSG)]
DispatchMessageW.restype = ctypes.c_ssize_t
