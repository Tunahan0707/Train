import ctypes



WS_OVERLAPPED = 0x00000000
WS_CAPTION = 0x00C00000
WS_SYSMENU = 0x00080000
WS_THICKFRAME = 0x00040000
WS_MINIMIZEBOX = 0x00020000
WS_MAXIMIZEBOX = 0x00010000
WM_DESTROY = 0x0002

SW_SHOW = 1
user32 = ctypes.WinDLL("user32.dll", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32.dll", use_last_error=True)
def_window_proc = user32.DefWindowProcW
def_window_proc.argtypes = [
    ctypes.c_void_p,
    ctypes.c_uint,
    ctypes.c_size_t,
    ctypes.c_ssize_t
]
def_window_proc.restype = ctypes.c_ssize_t

post_quit_message = user32.PostQuitMessage
post_quit_message.argtypes = [ctypes.c_int]
post_quit_message.restype = None

def window_procedure(hwnd, msg, wparam, lparam):
    if msg == WM_DESTROY:
        post_quit_message(0)
        return 0

    return def_window_proc(hwnd, msg, wparam, lparam)

WNDPROC = ctypes.WINFUNCTYPE(
    ctypes.c_ssize_t,
    ctypes.c_void_p,
    ctypes.c_uint,
    ctypes.c_size_t,
    ctypes.c_ssize_t
)

window_procedure = WNDPROC(window_procedure)



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


window_class = WNDClass()
window_class.style = 0
window_class.cbClsExtra = 0
window_class.cbWndExtra = 0
window_class.hIcon = None
window_class.hCursor = None
window_class.hbrBackground = None
window_class.lpszMenuName = None
window_class.lpfnWndProc = window_procedure
window_class.lpszClassName = "MyRendererWindow"

get_module_handle = kernel32.GetModuleHandleW
get_module_handle.restype = ctypes.c_void_p
get_module_handle.argtypes = [ctypes.c_wchar_p]

window_class.hInstance = get_module_handle(None)

register_class = user32.RegisterClassW
register_class.argtypes = [ctypes.POINTER(WNDClass)]
register_class.restype = ctypes.c_ushort

atom = register_class(ctypes.byref(window_class))

create_window = user32.CreateWindowExW
create_window.argtypes = [
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
create_window.restype = ctypes.c_void_p

show_window = user32.ShowWindow
show_window.argtypes = [
    ctypes.c_void_p,
    ctypes.c_int
]
show_window.restype = ctypes.c_int

WS_OVERLAPPEDWINDOW = (
    WS_OVERLAPPED
    | WS_CAPTION
    | WS_SYSMENU
    | WS_THICKFRAME
    | WS_MINIMIZEBOX
    | WS_MAXIMIZEBOX
)

hwnd = create_window(
    0,
    window_class.lpszClassName,
    "Porno??",
    WS_OVERLAPPEDWINDOW,
    100,
    100,
    800,
    600,
    None,
    None,
    window_class.hInstance,
    None
)

msg = MSG()

show_window(hwnd, SW_SHOW)

get_message = user32.GetMessageW
get_message.argtypes = [
    ctypes.POINTER(MSG),
    ctypes.c_void_p,
    ctypes.c_uint,
    ctypes.c_uint
]
get_message.restype = ctypes.c_int

translate_message = user32.TranslateMessage
translate_message.argtypes = [ctypes.POINTER(MSG)]
translate_message.restype = ctypes.c_int

dispatch_message = user32.DispatchMessageW
dispatch_message.argtypes = [ctypes.POINTER(MSG)]
dispatch_message.restype = ctypes.c_ssize_t
while True:
    result = get_message(
        ctypes.byref(msg),
        None,
        0,
        0
    )

    if result == -1:
        raise ctypes.WinError(ctypes.get_last_error())

    if result == 0:
        break

    translate_message(ctypes.byref(msg))
    dispatch_message(ctypes.byref(msg))

